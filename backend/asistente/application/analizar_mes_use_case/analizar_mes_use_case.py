# asistente/application/analizar_mes_use_case/analizar_mes_use_case.py — el análisis del mes (módulo 105)
"""Un trabajo largo (un minuto, una decena de llamadas al modelo), en una tarea de Celery, con un ORQUESTADOR y sus
ESPECIALISTAS (subagentes):

1. el contexto sale del usuario y el hogar de quien lo pidió (como una pregunta: Actor LECTOR, el día del hogar);
2. el orquestador reparte encargos a los especialistas (SubagenteTool), que trabajan cada uno con sus tools;
3. cada paso sale como aviso de progreso (el WebSocket de la app) con el id de la tarea;
4. el informe se guarda como una conversación nueva ("Análisis de octubre de 2026"), que se sigue en el chat; si los
   especialistas han leído texto de terceros, con su marca (módulo 102: en ella no se guardan recuerdos);
5. lo gastado, en el libro de cuentas (canal "analisis"), también si falla a mitad.
"""

import logging
from collections.abc import Callable

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.analizar_mes_use_case.dtos.analizar_mes_input_dto import AnalizarMesInputDTO
from asistente.application.analizar_mes_use_case.i_analizar_mes_use_case import IAnalizarMesUseCase
from asistente.application.chat.contador_de_uso import ContadorDeUso
from asistente.application.ports.i_avisos_de_progreso import IAvisosDeProgreso
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.ports.i_tarifas import ITarifas
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.repositories.i_consumo_repository import IConsumoRepository
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from asistente.domain.services.fechas_en_castellano import mes_largo
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.vo.mes import Mes

logger = logging.getLogger(__name__)
ESPECIALISTAS = {"especialista_gastos": "el gasto", "especialista_presupuestos": "los presupuestos",
                 "especialista_comercios": "los comercios"}  # fmt: skip


class ObservadorDelAnalisis(IObservadorAgente):
    """Los pasos que importan a quien espera: qué especialista empieza y cuál termina."""

    def __init__(self, avisar: Callable[[dict], None]):
        self.avisar = avisar

    def respuesta(self, respuesta):
        pass

    def llamada(self, llamada):
        if llamada.nombre in ESPECIALISTAS:
            self.avisar({"estado": "en_curso", "paso": f"Analizando {ESPECIALISTAS[llamada.nombre]}"})

    def resultado(self, resultado, duracion_ms):
        if resultado.nombre in ESPECIALISTAS:
            self.avisar({"estado": "en_curso", "paso": f"Listo: {ESPECIALISTAS[resultado.nombre]}"})


class AnalizarMesUseCase(IAnalizarMesUseCase):
    def __init__(
        self,
        *,
        crear_orquestador: Callable[[IObservadorAgente], Agente],  # el orquestador, con sus especialistas
        conversaciones: IConversacionCommandRepository,
        membresias: IMembresias,
        avisos: IAvisosDeProgreso,
        consumos: IConsumoRepository,
        tarifas: ITarifas,
        reloj: IReloj,
        uow: IUnidadDeTrabajo,
    ):
        self.crear_orquestador, self.conversaciones, self.membresias = crear_orquestador, conversaciones, membresias
        self.avisos, self.consumos, self.tarifas, self.reloj, self.uow = avisos, consumos, tarifas, reloj, uow

    def ejecutar(self, entrada: AnalizarMesInputDTO) -> int | None:
        def avisar(datos: dict) -> None:
            self.avisos.avisar(entrada.usuario_id, entrada.hogar_id, entrada.tarea, datos)

        contexto = ContextoPregunta.abrir(
            usuario_id=entrada.usuario_id, hogar_id=entrada.hogar_id, membresias=self.membresias, reloj=self.reloj
        )
        mes = Mes.desde_texto(entrada.mes)
        pregunta = f"Prepara el análisis de {mes_largo(mes)}."  # "…de septiembre de 2026 (2026-09)."
        avisar({"estado": "en_curso", "paso": "Repartiendo el trabajo"})
        contador = ContadorDeUso(ObservadorDelAnalisis(avisar), con_ayuda=False)
        try:
            r = self.crear_orquestador(contador).responder((Mensaje.usuario(pregunta),), contexto)
        except LLMException:
            logger.warning("Análisis sin terminar: el LLM no está disponible", exc_info=True)
            avisar({"estado": "fallido", "paso": "El asistente no está disponible ahora mismo."})
            return None
        finally:
            consumos = contador.consumos(
                usuario_id=entrada.usuario_id,
                hogar_id=entrada.hogar_id,
                conversacion_id=None,
                canal=CanalDeConsumo.ANALISIS,
                tarifas=self.tarifas,
                momento=self.reloj.ahora(),
            )
            if consumos:
                with self.uow:
                    self.consumos.anotar(consumos)
        if r.motivo != MotivoParada.FIN:
            avisar({"estado": "fallido", "paso": "No he podido terminar el análisis."})
            return None
        conversacion = Conversacion(entrada.usuario_id, entrada.hogar_id)
        conversacion.titular(f"Análisis de {mes_largo(mes).removesuffix(f' ({mes})')}")
        if r.terceros:  # módulo 102: los especialistas han leído terceros, y el informe puede repetirlo
            conversacion.marcar_con_terceros()
        with self.uow:
            self.conversaciones.guardar(conversacion)
            self.conversaciones.anadir(
                conversacion.id,
                [  # solo la pregunta y el informe: el trabajo de los especialistas no viaja a la conversación
                    MensajeDeConversacion(Mensaje.usuario(pregunta), visible=True, texto=pregunta),
                    MensajeDeConversacion(Mensaje.modelo(texto=r.texto), visible=True, texto=r.texto),
                ],
            )
        avisar({"estado": "terminado", "paso": "Análisis listo", "conversacion": conversacion.id})
        return conversacion.id
