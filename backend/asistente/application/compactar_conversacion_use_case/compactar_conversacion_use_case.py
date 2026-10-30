# asistente/application/compactar_conversacion_use_case/compactar_conversacion_use_case.py (módulo 99)
"""La compactación: cuando lo que una conversación lleva sin resumir pasa de un umbral, lo antiguo (todo menos los
últimos intercambios) se resume con el modelo AUXILIAR y el resumen sustituye a esas preguntas en lo que viaja.

    [resumen de 1..6]  +  7 (pregunta y respuesta)  +  8  +  la pregunta nueva

Frente a quitar lo antiguo (ventana, módulo 96), el resumen conserva lo importante ("en septiembre, 776,59 €") en
pocos tokens; a cambio, una llamada más (después de la respuesta: nadie la espera) y una pérdida que no se ve: lo que
el resumen no cuenta, el modelo no lo sabe. Por eso el resumen es incremental (el nuevo incluye el anterior) y se
conservan siempre los últimos intercambios enteros: la pregunta siguiente suele ir sobre ellos.
"""

import logging

from asistente.application.compactar_conversacion_use_case.dtos.compactar_conversacion_input_dto import (
    CompactarConversacionInputDTO,
)
from asistente.application.compactar_conversacion_use_case.i_compactar_conversacion_use_case import (
    ICompactarConversacionUseCase,
)
from asistente.application.ports.i_llm import ILLM
from asistente.application.ports.i_tarifas import ITarifas
from asistente.application.prompts.memoria import RESUMIR
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.repositories.i_consumo_repository import IConsumoRepository
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from asistente.domain.services.tokens import estimar_tokens
from asistente.domain.vo.consumo import Consumo
from asistente.domain.vo.intercambio import Intercambio
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo

logger = logging.getLogger(__name__)
PALABRAS = 150


class CompactarConversacionUseCase(ICompactarConversacionUseCase):
    def __init__(
        self,
        *,
        conversaciones: IConversacionCommandRepository,
        llm: ILLM,  # el auxiliar: resumir es fácil y no debe gastar la cuota del modelo grande
        consumos: IConsumoRepository,
        tarifas: ITarifas,
        reloj: IReloj,
        uow: IUnidadDeTrabajo,
        umbral: int = 1500,  # tokens estimados sin resumir a partir de los que se resume (la ventana es de 3.000)
        conservar: int = 2,  # intercambios recientes que nunca se resumen
    ):
        self.conversaciones, self.llm, self.consumos, self.tarifas = conversaciones, llm, consumos, tarifas
        self.reloj, self.uow, self.umbral, self.conservar = reloj, uow, umbral, conservar

    def ejecutar(self, entrada: CompactarConversacionInputDTO) -> bool:
        conversacion = self.conversaciones.obtener(entrada.usuario_id, entrada.hogar_id, entrada.conversacion_id)
        intercambios = self.conversaciones.intercambios(conversacion.id, conversacion.resumido_hasta)
        if len(intercambios) <= self.conservar or _tokens(intercambios) < self.umbral:
            return False
        a_resumir = intercambios[: -self.conservar]
        anterior = (
            f"Resumen de lo anterior (inclúyelo):\n<resumen>\n{conversacion.resumen}\n</resumen>\n"
            if conversacion.resumen
            else ""
        )
        texto = RESUMIR.rellenar(palabras=PALABRAS, anterior=anterior, conversacion=_en_texto(a_resumir))
        peticion = PeticionLLM(
            sistema="",
            mensajes=(Mensaje.usuario(texto),),
            esfuerzo=EsfuerzoDeRazonamiento.BAJO,
            max_tokens=PALABRAS * 3 + 300,  # el razonamiento también cuenta
        )
        try:
            r = self.llm.generar(peticion)
        except LLMException:  # se intentará tras la próxima respuesta: mientras, la ventana quita lo antiguo
            logger.warning("Sin resumen: el LLM no está disponible", exc_info=True)
            return False
        precio = self.tarifas.precio(r.modelo)
        consumo = Consumo(
            entrada.usuario_id, entrada.hogar_id, CanalDeConsumo.RESUMEN, r.modelo, r.uso,
            precio.coste(r.uso) if precio else None, self.reloj.ahora(), conversacion.id,
        )  # fmt: skip
        if r.motivo != MotivoFin.FIN or not r.texto.strip():  # cortado o vacío: mejor sin resumen que uno a medias
            with self.uow:
                self.consumos.anotar([consumo])
            return False
        conversacion.resumir(r.texto, a_resumir[-1].hasta)
        with self.uow:
            self.consumos.anotar([consumo])
            self.conversaciones.guardar_resumen(conversacion)
        logger.info("Conversación %s resumida hasta el mensaje %s", conversacion.id, conversacion.resumido_hasta)
        return True


def _tokens(intercambios) -> int:
    return sum(estimar_tokens(i.pregunta) + estimar_tokens(i.respuesta) for i in intercambios)


def _en_texto(intercambios: tuple[Intercambio, ...]) -> str:
    return "\n".join(f"Persona: {i.pregunta}\nAsistente: {i.respuesta}" for i in intercambios)
