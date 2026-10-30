# asistente/application/responder_pregunta_use_case/responder_pregunta_use_case.py — el chat, de punta a punta (módulos 97 a 99)
"""Una pregunta en una conversación guardada:

1. la conversación es de quien pregunta (si no, 404) y el contexto sale de la sesión (hogar, Actor LECTOR, "hoy"); si
   ha agotado su cuota (módulo 98), CuotaAgotadaException;
2. si hay adjunto, se guarda y su texto (OCR) entra en la pregunta, marcado como no fiable;
3. la pregunta se guarda ANTES de llamar al modelo: si algo falla, se ve qué se preguntó;
4. el agente responde con el historial, en streaming; cada paso sale por el emisor (ObservadorDelChat), y un archivo
   exportado queda ligado a la pregunta en cuanto se guarda (si la pregunta no termina, se borra con la conversación);
5. la respuesta se guarda con sus turnos intermedios (ocultos), los artefactos y las preguntas de seguimiento;
6. tras la primera respuesta, el título, con el modelo auxiliar;
7. lo gastado, por modelo, se apunta SIEMPRE (también si se cancela o falla a mitad): se ha pagado (módulo 98);
8. módulo 99: viaja con la memoria (los recuerdos de la persona y el resumen de lo antiguo), y al terminar se programa
   la compactación (resumir lo antiguo, si hace falta, fuera de la respuesta).

Cancelada o sin modelo disponible, la pregunta queda "incompleta": se ve en el chat, pero ya no viaja al modelo.
"""

import logging
from collections.abc import Callable
from dataclasses import replace
from typing import Any

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.memoria import memoria
from asistente.application.agent.observador_mudo import ObservadorMudo
from asistente.application.agent.resultado_agente import ResultadoAgente
from asistente.application.chat.adjunto import MAX_BYTES, TIPOS, con_adjunto
from asistente.application.chat.contador_de_uso import ContadorDeUso
from asistente.application.chat.observador_del_chat import ObservadorDelChat
from asistente.application.chat.titular import titular
from asistente.application.cuotas.calcular_cuota import calcular_cuota
from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos
from asistente.application.ports.i_lector_de_adjuntos import ILectorDeAdjuntos
from asistente.application.ports.i_llm import ILLM
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.ports.i_programador_de_compactacion import IProgramadorDeCompactacion
from asistente.application.ports.i_tarifas import ITarifas
from asistente.application.responder_pregunta_use_case.dtos.responder_pregunta_input_dto import (
    ResponderPreguntaInputDTO,
)
from asistente.application.responder_pregunta_use_case.i_responder_pregunta_use_case import (
    IResponderPreguntaUseCase,
)
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.bo.propuesta import Propuesta
from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.enums.rol_mensaje import RolMensaje
from asistente.domain.exceptions.adjunto_no_valido_exception import AdjuntoNoValidoException
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.exceptions.pregunta_cancelada_exception import PreguntaCanceladaException
from asistente.domain.repositories.i_consumo_query_service import IConsumoQueryService
from asistente.domain.repositories.i_consumo_repository import IConsumoRepository
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from asistente.domain.repositories.i_plan_del_hogar_repository import IPlanDelHogarRepository
from asistente.domain.repositories.i_propuesta_command_repository import IPropuestaCommandRepository
from asistente.domain.repositories.i_recuerdo_query_service import IRecuerdoQueryService
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.mensaje_de_conversacion import MensajeDeConversacion
from asistente.domain.vo.propuesta_preparada import PropuestaPreparada
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol

logger = logging.getLogger(__name__)
NO_DISPONIBLE = "El asistente no está disponible ahora mismo. Inténtalo dentro de un momento."


class ResponderPreguntaUseCase(IResponderPreguntaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        conversaciones: IConversacionCommandRepository,
        propuestas: IPropuestaCommandRepository,
        crear_agente: Callable[[IObservadorAgente], Agente],  # el agente del chat, con el observador de ESTA pregunta
        llm_auxiliar: ILLM,  # el modelo pequeño: el título
        membresias: IMembresias,
        lector: ILectorDeAdjuntos,
        almacen: IAlmacenDeArchivos,
        reloj: IReloj,
        uow: IUnidadDeTrabajo,
        # Módulo 98: las cuotas y el libro de cuentas
        planes: IPlanDelHogarRepository,
        tarifas: ITarifas,
        consumos: IConsumoRepository,
        consultas_de_consumo: IConsumoQueryService,
        # Módulo 99: la memoria
        recuerdos: IRecuerdoQueryService,
        compactacion: IProgramadorDeCompactacion,
    ):
        self.conversaciones, self.propuestas, self.crear_agente = conversaciones, propuestas, crear_agente
        self.llm_auxiliar, self.membresias, self.lector, self.almacen = llm_auxiliar, membresias, lector, almacen
        self.reloj, self.uow = reloj, uow
        self.planes, self.tarifas, self.consumos, self.consultas_de_consumo = (
            planes,
            tarifas,
            consumos,
            consultas_de_consumo,
        )
        self.recuerdos, self.compactacion = recuerdos, compactacion

    def ejecutar(self, entrada: ResponderPreguntaInputDTO) -> int | None:
        entrada.actor.exigir(self.rol_minimo)
        usuario_id, emisor = entrada.actor.usuario_id, entrada.emisor
        conversacion = self.conversaciones.obtener(usuario_id, entrada.hogar_id, entrada.conversacion_id)
        contexto = ContextoPregunta.abrir(
            usuario_id=usuario_id, hogar_id=entrada.hogar_id, membresias=self.membresias, reloj=self.reloj
        )
        contexto = replace(contexto, conversacion_id=conversacion.id)
        calcular_cuota(
            contexto,
            self.reloj.ahora(),
            planes=self.planes,
            tarifas=self.tarifas,
            consumos=self.consultas_de_consumo,
        ).exigir(self.reloj.ahora())
        historial = self.conversaciones.historial(conversacion.id, conversacion.resumido_hasta)
        recuerdos = [r.texto for r in self.recuerdos.listar(usuario_id, entrada.hogar_id)]
        pregunta = self._pregunta(entrada)
        with self.uow:
            (pregunta_id,) = self.conversaciones.anadir(conversacion.id, [pregunta])
            self.conversaciones.guardar(conversacion)  # sube al principio de la lista
        emisor.emitir("inicio", {"conversacion": conversacion.id, "pregunta": pregunta_id})

        observador = ObservadorDelChat(
            emisor,
            self.almacen,
            lambda p: self._guardar_propuesta(p, conversacion, usuario_id),
            lambda ruta: self._ligar_archivo(pregunta_id, ruta),
        )
        contador = ContadorDeUso(observador)
        try:
            r = self.crear_agente(contador).responder(
                (*historial, pregunta.mensaje),
                contexto,
                estructurada=True,
                al_texto=observador.texto,
                memoria=memoria(conversacion.resumen, recuerdos),
            )
        except PreguntaCanceladaException:
            logger.info("Pregunta cancelada (conversación %s)", conversacion.id)
            self.conversaciones.marcar_incompleto(pregunta_id, "cancelada")
            return None
        except LLMException:
            logger.warning("Sin respuesta: el LLM no está disponible", exc_info=True)
            self.conversaciones.marcar_incompleto(pregunta_id, "sin_modelo")
            emisor.emitir("error", {"detalle": NO_DISPONIBLE})
            return None
        except Exception:
            self.conversaciones.marcar_incompleto(pregunta_id, "error")  # un bug nuestro: no queda sin respuesta
            raise
        finally:
            self._apuntar(contador, contexto, CanalDeConsumo.CHAT)
            self._apuntar(contador.ayuda, contexto, CanalDeConsumo.AYUDA)  # ejercicio 1 del 100

        titulo = None
        primera = not conversacion.resumen and not any(m.rol == RolMensaje.USUARIO for m in historial)
        if primera:  # la primera pregunta: el título
            titulo, respuesta_titulo = titular(self.llm_auxiliar, entrada.texto)
            del_titulo = ContadorDeUso(ObservadorMudo())
            del_titulo.sumar(respuesta_titulo)
            self._apuntar(del_titulo, contexto, CanalDeConsumo.TITULO)
        datos = self._datos(r, observador)
        with self.uow:
            mensajes = [MensajeDeConversacion(m) for m in r.nuevos[:-1]]  # tool calls y resultados: ocultos
            mensajes.append(MensajeDeConversacion(r.nuevos[-1], visible=True, texto=r.texto, datos=datos))
            ids = self.conversaciones.anadir(conversacion.id, mensajes)
            titulada = titulo is not None and conversacion.titular(titulo)
            self.conversaciones.guardar(conversacion)
            self.compactacion.programar(usuario_id, entrada.hogar_id, conversacion.id)  # tras el commit, aparte
        if titulada:
            emisor.emitir("titulo", {"titulo": conversacion.titulo})
        emisor.emitir("fin", {"mensaje": ids[-1], "texto": r.texto, **datos})
        return ids[-1]

    def _apuntar(self, contador: ContadorDeUso, contexto: ContextoPregunta, canal: CanalDeConsumo) -> None:
        consumos = contador.consumos(
            usuario_id=contexto.usuario_id,
            hogar_id=contexto.hogar.id,
            conversacion_id=contexto.conversacion_id,
            canal=canal,
            tarifas=self.tarifas,
            momento=self.reloj.ahora(),
        )
        if consumos:
            with self.uow:
                self.consumos.anotar(consumos)

    def _pregunta(self, entrada: ResponderPreguntaInputDTO) -> MensajeDeConversacion:
        """La pregunta que viaja al modelo y la que se ve: distintas si hay adjunto (el modelo lee también su texto)."""
        adjunto = entrada.adjunto
        if adjunto is None:
            return MensajeDeConversacion(Mensaje.usuario(entrada.texto), visible=True, texto=entrada.texto)
        if adjunto.tipo not in TIPOS or not 0 < len(adjunto.contenido) <= MAX_BYTES:
            raise AdjuntoNoValidoException()
        entrada.emisor.emitir("tool", {"nombre": "adjunto", "texto": "Leyendo el adjunto"})
        ruta = self.almacen.guardar(f"asistente/{entrada.hogar_id}", adjunto.contenido)
        texto = con_adjunto(entrada.texto, self.lector.leer(adjunto.contenido, adjunto.tipo), adjunto.nombre)
        return MensajeDeConversacion(
            Mensaje.usuario(texto),
            visible=True,
            texto=entrada.texto,
            adjunto=ruta,
            nombre_adjunto=adjunto.nombre[:255],
        )

    def _ligar_archivo(self, pregunta_id: int, ruta: str) -> None:
        with self.uow:
            self.conversaciones.ligar_archivo(pregunta_id, ruta)

    def _guardar_propuesta(self, p: PropuestaPreparada, conversacion: Conversacion, usuario_id: int) -> dict[str, Any]:
        propuesta = Propuesta(
            conversacion.id, usuario_id, conversacion.hogar_id, p.tipo, p.resumen, dict(p.datos), self.reloj.ahora()
        )
        with self.uow:
            self.propuestas.guardar(propuesta)
        return {"id": propuesta.id, "tipo": str(p.tipo), "resumen": p.resumen}

    @staticmethod
    def _datos(r: ResultadoAgente, observador: ObservadorDelChat) -> dict[str, Any]:
        """Lo que la interfaz pinta junto a la respuesta (y lo que vuelve a pintar al abrir la conversación)."""
        return {
            "graficos": observador.graficos,
            "archivos": observador.archivos,
            "propuestas": observador.propuestas,
            "recuerdos": observador.recuerdos,
            "fuentes": observador.fuentes,  # ejercicio 2 del 100
            "consultas": observador.consultas,  # módulo 101
            "seguimiento": list(r.estructurada.seguimiento) if r.estructurada else [],
            "motivo": str(r.motivo),
            "uso": {
                "entrada": r.uso.entrada,
                "salida": r.uso.salida,
                "cache": r.uso.cache,
                "vueltas": r.iteraciones,
                "modelos": list(dict.fromkeys(r.modelos)),
                "ms": r.duracion_ms,
            },
        }
