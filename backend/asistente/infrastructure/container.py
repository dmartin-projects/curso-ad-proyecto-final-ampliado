# asistente/infrastructure/container.py — composition root del asistente (módulos 93, 94, 95 y 97)
#
# El único sitio que decide QUÉ adapters se usan y con qué ajustes: el LLM (con su reserva), las tools con sus ports y
# el contexto de una pregunta. El resto recibe las piezas ya montadas; los tests pasan fakes y no llegan nunca aquí.
import functools
from collections.abc import Callable

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.agent.limites import Limites
from asistente.application.asignar_plan_use_case.asignar_plan_use_case import AsignarPlanUseCase
from asistente.application.asignar_plan_use_case.i_asignar_plan_use_case import IAsignarPlanUseCase
from asistente.application.ayuda.buscador_de_ayuda import BuscadorDeAyuda
from asistente.application.chat.calculadora_de_graficos import CalculadoraDeGraficos
from asistente.application.compactar_conversacion_use_case.compactar_conversacion_use_case import (
    CompactarConversacionUseCase,
)
from asistente.application.compactar_conversacion_use_case.i_compactar_conversacion_use_case import (
    ICompactarConversacionUseCase,
)
from asistente.application.confirmar_propuesta_use_case.confirmar_propuesta_use_case import ConfirmarPropuestaUseCase
from asistente.application.confirmar_propuesta_use_case.i_confirmar_propuesta_use_case import (
    IConfirmarPropuestaUseCase,
)
from asistente.application.consultar_cuota_use_case.consultar_cuota_use_case import ConsultarCuotaUseCase
from asistente.application.consultar_cuota_use_case.i_consultar_cuota_use_case import IConsultarCuotaUseCase
from asistente.application.contar_hogares_sin_cuota_use_case.contar_hogares_sin_cuota_use_case import (
    ContarHogaresSinCuotaUseCase,
)
from asistente.application.contar_hogares_sin_cuota_use_case.i_contar_hogares_sin_cuota_use_case import (
    IContarHogaresSinCuotaUseCase,
)
from asistente.application.crear_carpeta_use_case.crear_carpeta_use_case import CrearCarpetaUseCase
from asistente.application.crear_carpeta_use_case.i_crear_carpeta_use_case import ICrearCarpetaUseCase
from asistente.application.crear_conversacion_use_case.crear_conversacion_use_case import CrearConversacionUseCase
from asistente.application.crear_conversacion_use_case.i_crear_conversacion_use_case import (
    ICrearConversacionUseCase,
)
from asistente.application.descartar_propuesta_use_case.descartar_propuesta_use_case import DescartarPropuestaUseCase
from asistente.application.descartar_propuesta_use_case.i_descartar_propuesta_use_case import (
    IDescartarPropuestaUseCase,
)
from asistente.application.eliminar_carpeta_use_case.eliminar_carpeta_use_case import EliminarCarpetaUseCase
from asistente.application.eliminar_carpeta_use_case.i_eliminar_carpeta_use_case import IEliminarCarpetaUseCase
from asistente.application.eliminar_conversacion_use_case.eliminar_conversacion_use_case import (
    EliminarConversacionUseCase,
)
from asistente.application.eliminar_conversacion_use_case.i_eliminar_conversacion_use_case import (
    IEliminarConversacionUseCase,
)
from asistente.application.fijar_grafico_use_case.fijar_grafico_use_case import FijarGraficoUseCase
from asistente.application.fijar_grafico_use_case.i_fijar_grafico_use_case import IFijarGraficoUseCase
from asistente.application.indexar_ayuda_use_case.i_indexar_ayuda_use_case import IIndexarAyudaUseCase
from asistente.application.indexar_ayuda_use_case.indexar_ayuda_use_case import IndexarAyudaUseCase
from asistente.application.informe_de_costes_use_case.i_informe_de_costes_use_case import IInformeDeCostesUseCase
from asistente.application.informe_de_costes_use_case.informe_de_costes_use_case import InformeDeCostesUseCase
from asistente.application.listar_carpetas_use_case.i_listar_carpetas_use_case import IListarCarpetasUseCase
from asistente.application.listar_carpetas_use_case.listar_carpetas_use_case import ListarCarpetasUseCase
from asistente.application.listar_conversaciones_use_case.i_listar_conversaciones_use_case import (
    IListarConversacionesUseCase,
)
from asistente.application.listar_conversaciones_use_case.listar_conversaciones_use_case import (
    ListarConversacionesUseCase,
)
from asistente.application.listar_graficos_fijados_use_case.i_listar_graficos_fijados_use_case import (
    IListarGraficosFijadosUseCase,
)
from asistente.application.listar_graficos_fijados_use_case.listar_graficos_fijados_use_case import (
    ListarGraficosFijadosUseCase,
)
from asistente.application.listar_recuerdos_use_case.i_listar_recuerdos_use_case import IListarRecuerdosUseCase
from asistente.application.listar_recuerdos_use_case.listar_recuerdos_use_case import ListarRecuerdosUseCase
from asistente.application.modificar_carpeta_use_case.i_modificar_carpeta_use_case import IModificarCarpetaUseCase
from asistente.application.modificar_carpeta_use_case.modificar_carpeta_use_case import ModificarCarpetaUseCase
from asistente.application.modificar_conversacion_use_case.i_modificar_conversacion_use_case import (
    IModificarConversacionUseCase,
)
from asistente.application.modificar_conversacion_use_case.modificar_conversacion_use_case import (
    ModificarConversacionUseCase,
)
from asistente.application.obtener_conversacion_use_case.i_obtener_conversacion_use_case import (
    IObtenerConversacionUseCase,
)
from asistente.application.obtener_conversacion_use_case.obtener_conversacion_use_case import (
    ObtenerConversacionUseCase,
)
from asistente.application.olvidar_recuerdo_use_case.i_olvidar_recuerdo_use_case import IOlvidarRecuerdoUseCase
from asistente.application.olvidar_recuerdo_use_case.olvidar_recuerdo_use_case import OlvidarRecuerdoUseCase
from asistente.application.ports.i_embeddings import IEmbeddings
from asistente.application.ports.i_llm import ILLM
from asistente.application.ports.i_observador_agente import IObservadorAgente
from asistente.application.quitar_grafico_use_case.i_quitar_grafico_use_case import IQuitarGraficoUseCase
from asistente.application.quitar_grafico_use_case.quitar_grafico_use_case import QuitarGraficoUseCase
from asistente.application.responder_pregunta_use_case.i_responder_pregunta_use_case import (
    IResponderPreguntaUseCase,
)
from asistente.application.responder_pregunta_use_case.responder_pregunta_use_case import ResponderPreguntaUseCase
from asistente.application.seguridad.vigilante import Vigilante
from asistente.application.tools.buscar_ayuda_tool import BuscarAyudaTool
from asistente.application.tools.buscar_movimientos_tool import BuscarMovimientosTool
from asistente.application.tools.comparar_con_ipc_tool import CompararConIpcTool
from asistente.application.tools.comparar_meses_tool import CompararMesesTool
from asistente.application.tools.consultar_sql_tool import ConsultarSQLTool
from asistente.application.tools.detalle_ticket_tool import DetalleTicketTool
from asistente.application.tools.dias_festivos_tool import DiasFestivosTool
from asistente.application.tools.estado_presupuestos_tool import EstadoPresupuestosTool
from asistente.application.tools.exportar_tool import ExportarTool
from asistente.application.tools.gasto_por_categoria_tool import GastoPorCategoriaTool
from asistente.application.tools.grafico_tool import GraficoTool
from asistente.application.tools.listar_categorias_tool import ListarCategoriasTool
from asistente.application.tools.listar_cuentas_tool import ListarCuentasTool
from asistente.application.tools.listar_miembros_tool import ListarMiembrosTool
from asistente.application.tools.olvidar_tool import OlvidarTool
from asistente.application.tools.prevision_fin_de_mes_tool import PrevisionFinDeMesTool
from asistente.application.tools.proponer_movimiento_tool import ProponerMovimientoTool
from asistente.application.tools.recordar_tool import RecordarTool
from asistente.application.tools.resumen_mes_tool import ResumenMesTool
from asistente.application.tools.tendencia_tool import TendenciaTool
from asistente.application.tools.tipo_de_cambio_tool import TipoDeCambioTool
from asistente.application.tools.tool import Tool
from asistente.application.tools.top_comercios_tool import TopComerciosTool
from asistente.application.ver_contexto_use_case.i_ver_contexto_use_case import IVerContextoUseCase
from asistente.application.ver_contexto_use_case.ver_contexto_use_case import VerContextoUseCase
from asistente.domain.vo.precio import Precio
from asistente.infrastructure.ayuda.fuente_de_ayuda_en_disco import FuenteDeAyudaEnDisco
from asistente.infrastructure.database.repositories.carpeta_command_repository_orm import CarpetaCommandRepositoryORM
from asistente.infrastructure.database.repositories.consumo_query_service_orm import ConsumoQueryServiceORM
from asistente.infrastructure.database.repositories.consumo_repository_orm import ConsumoRepositoryORM
from asistente.infrastructure.database.repositories.conversacion_command_repository_orm import (
    ConversacionCommandRepositoryORM,
)
from asistente.infrastructure.database.repositories.conversacion_query_service_orm import ConversacionQueryServiceORM
from asistente.infrastructure.database.repositories.grafico_fijado_command_repository_orm import (
    GraficoFijadoCommandRepositoryORM,
)
from asistente.infrastructure.database.repositories.grafico_fijado_query_service_orm import (
    GraficoFijadoQueryServiceORM,
)
from asistente.infrastructure.database.repositories.indice_de_ayuda_pg import IndiceDeAyudaPG
from asistente.infrastructure.database.repositories.plan_del_hogar_repository_orm import PlanDelHogarRepositoryORM
from asistente.infrastructure.database.repositories.propuesta_command_repository_orm import (
    PropuestaCommandRepositoryORM,
)
from asistente.infrastructure.database.repositories.recuerdo_command_repository_orm import RecuerdoCommandRepositoryORM
from asistente.infrastructure.database.repositories.recuerdo_query_service_orm import RecuerdoQueryServiceORM
from asistente.infrastructure.embeddings.embeddings_fastembed import EmbeddingsFastembed
from asistente.infrastructure.externos.eurostat_indice_de_precios import IndiceDePreciosEurostat
from asistente.infrastructure.externos.frankfurter_tipo_de_cambio import TipoDeCambioFrankfurter
from asistente.infrastructure.externos.nager_festivos import FestivosNager
from asistente.infrastructure.finanzas.consultas_en_finanzas import ConsultasEnFinanzas
from asistente.infrastructure.finanzas.ejecutor_de_propuestas_en_finanzas import EjecutorDePropuestasEnFinanzas
from asistente.infrastructure.finanzas.exportador_en_finanzas import ExportadorEnFinanzas
from asistente.infrastructure.hogares.membresias_en_hogares import MembresiasEnHogares
from asistente.infrastructure.llm.cliente_openai import cliente_del_proceso
from asistente.infrastructure.llm.detector_con_politica import DetectorConPolitica
from asistente.infrastructure.llm.detector_prompt_guard import DetectorPromptGuard
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM
from asistente.infrastructure.messaging.programador_de_compactacion_celery import ProgramadorDeCompactacionCelery
from asistente.infrastructure.sql.consultas_sql_postgres import ConsultasSQLPostgres
from asistente.infrastructure.storage.almacen_django import AlmacenDjango
from asistente.infrastructure.tarifas.tarifas_desde_ajustes import TarifasDesdeAjustes
from asistente.infrastructure.telemetria import instrumentos
from asistente.infrastructure.telemetria.llm_medido import LLMMedido
from asistente.infrastructure.telemetria.telemetria_otel import TelemetriaOTel
from asistente.infrastructure.tickets.lector_de_adjuntos_en_tickets import LectorDeAdjuntosEnTickets
from asistente.infrastructure.tickets.tickets_en_tickets import TicketsEnTickets
from core.application.ports.i_reloj import IReloj
from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.clock.reloj_django import RelojDjango
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango


def llm(modelo: str | None = None) -> ILLM:
    """El principal con su reserva (módulo 94); con `modelo`, solo ese (probar_llm --modelo)."""
    if not settings.ASISTENTE_API_KEY:  # mejor esto al arrancar que un 401 en mitad de una conversación
        raise ImproperlyConfigured("Falta ASISTENTE_API_KEY: el asistente no puede hablar con ningún modelo.")
    if modelo:
        return _medido(modelo)
    modelos = [settings.ASISTENTE_MODELO, *settings.ASISTENTE_MODELOS_RESERVA]
    return LLMConReserva([(_medido(m), _circuito(m)) for m in modelos])


def llm_auxiliar() -> ILLM:
    """Módulo 97: el modelo pequeño, para las tareas fáciles (el título de una conversación). Con su reserva: el
    principal (en Groq, cada modelo tiene su cuota: si el pequeño la agota, el grande suele tenerla)."""
    modelos = [settings.ASISTENTE_MODELO_AUXILIAR, settings.ASISTENTE_MODELO]
    return LLMConReserva([(_medido(m), _circuito(m)) for m in modelos])


def _medido(modelo: str) -> ILLM:
    """Módulo 98: cada modelo, medido (span y métricas GenAI de OpenTelemetry). Sin OTEL_ENABLED no cuesta nada: la API
    de OpenTelemetry sin SDK no hace nada."""
    cliente = cliente_del_proceso(settings.ASISTENTE_BASE_URL, settings.ASISTENTE_API_KEY, settings.ASISTENTE_TIMEOUT)
    return LLMMedido(
        OpenAICompatibleLLM(cliente=cliente, modelo=modelo),
        proveedor=settings.ASISTENTE_PROVEEDOR,
        base_url=settings.ASISTENTE_BASE_URL,
        precio=precio,
    )


def _circuito(modelo: str) -> CircuitBreaker:
    """Tres fallos transitorios seguidos (tras los reintentos del adapter) y ese modelo descansa 2 minutos. El estado
    vive en Redis: lo comparten todos los procesos, como el de la IA de los tickets."""
    return CircuitBreaker(f"llm:{modelo}", umbral=3, enfriamiento=120)


def precio(modelo: str) -> Precio | None:
    """None si el modelo no está en la tabla: mejor "coste desconocido" que un coste inventado."""
    return TarifasDesdeAjustes().precio(modelo)


def tools(chat: bool = False) -> list[Tool]:
    """El catálogo (módulo 95). El orden es el de la declaración: las más usadas, primero.

    Con `chat` (módulo 97), además las del canal del chat: las que producen algo que solo una interfaz puede enseñar
    (un gráfico, un archivo para descargar, una propuesta con su botón de confirmar). En la terminal no tendrían sentido.
    """
    finanzas = ConsultasEnFinanzas()
    consulta = _de_consulta(finanzas)
    if not chat:
        return consulta
    return [
        *consulta,
        GraficoTool(calculadora=CalculadoraDeGraficos(consulta)),
        ExportarTool(finanzas=finanzas, exportador=ExportadorEnFinanzas(almacen=AlmacenDjango())),
        ProponerMovimientoTool(finanzas=finanzas),
        RecordarTool(recuerdos=RecuerdoCommandRepositoryORM(), reloj=RelojDjango()),  # módulo 99
        OlvidarTool(recuerdos=RecuerdoCommandRepositoryORM(), consultas=RecuerdoQueryServiceORM()),  # su ejercicio 1
        BuscarAyudaTool(buscador=buscador_de_ayuda()),  # módulo 100
        *_text_to_sql(),  # módulo 101: solo si se enciende (ASISTENTE_TEXT_TO_SQL) y el rol tiene contraseña
    ]


def _de_consulta(finanzas: ConsultasEnFinanzas) -> list[Tool]:
    return [
        ResumenMesTool(finanzas=finanzas),
        GastoPorCategoriaTool(finanzas=finanzas),
        CompararMesesTool(finanzas=finanzas),  # ejercicio 2 del 95
        BuscarMovimientosTool(finanzas=finanzas),
        TendenciaTool(finanzas=finanzas),
        TopComerciosTool(finanzas=finanzas),
        EstadoPresupuestosTool(finanzas=finanzas),
        PrevisionFinDeMesTool(finanzas=finanzas),
        ListarCategoriasTool(finanzas=finanzas),
        DetalleTicketTool(tickets=TicketsEnTickets()),
        TipoDeCambioTool(divisas=_tipo_de_cambio(settings.ASISTENTE_FRANKFURTER_URL)),
        CompararConIpcTool(finanzas=finanzas, precios=_indice_de_precios(settings.ASISTENTE_EUROSTAT_URL)),
        DiasFestivosTool(festivos=_festivos(settings.ASISTENTE_NAGER_URL)),  # ejercicio 1 del 95
        ListarCuentasTool(finanzas=finanzas),  # módulo 97
        ListarMiembrosTool(membresias=MembresiasEnHogares()),
    ]


# Los adapters de servicios externos guardan su cliente HTTP (conexión abierta, TLS ya negociado): uno por proceso
@functools.lru_cache(maxsize=2)
def _tipo_de_cambio(base_url: str) -> TipoDeCambioFrankfurter:
    return TipoDeCambioFrankfurter(base_url=base_url)


@functools.lru_cache(maxsize=2)
def _indice_de_precios(base_url: str) -> IndiceDePreciosEurostat:
    return IndiceDePreciosEurostat(base_url=base_url)


@functools.lru_cache(maxsize=2)
def _festivos(base_url: str) -> FestivosNager:
    return FestivosNager(base_url=base_url)


def agente(observador: IObservadorAgente | None = None, modelo: str | None = None, chat: bool = False) -> Agente:
    limites = Limites(
        segundos=settings.ASISTENTE_SEGUNDOS_POR_PREGUNTA, max_tokens=settings.ASISTENTE_TOKENS_POR_PREGUNTA
    )
    return Agente(
        llm=llm(modelo),
        tools=tools(chat),
        limites=limites,
        observador=observador,
        telemetria=TelemetriaOTel(),
        vigilante=vigilante(),  # módulo 102
    )


def contexto(usuario_id: int, hogar_id: int, reloj: IReloj | None = None) -> ContextoPregunta:
    """`reloj`: otro momento (ejercicio 2 del 96: ver el prompt de otro día). Por defecto, el de Django."""
    return ContextoPregunta.abrir(
        usuario_id=usuario_id, hogar_id=hogar_id, membresias=MembresiasEnHogares(), reloj=reloj or RelojDjango()
    )


# ── Módulo 97: el chat ──
def _calculadora() -> CalculadoraDeGraficos:
    return CalculadoraDeGraficos(_de_consulta(ConsultasEnFinanzas()))


def responder_pregunta() -> IResponderPreguntaUseCase:
    return ResponderPreguntaUseCase(
        conversaciones=ConversacionCommandRepositoryORM(),
        propuestas=PropuestaCommandRepositoryORM(),
        crear_agente=lambda observador: agente(observador, chat=True),
        llm_auxiliar=llm_auxiliar(),
        membresias=MembresiasEnHogares(),
        lector=LectorDeAdjuntosEnTickets(),
        almacen=AlmacenDjango(),
        reloj=RelojDjango(),
        uow=UnidadDeTrabajoDjango(),
        planes=PlanDelHogarRepositoryORM(),
        tarifas=TarifasDesdeAjustes(),
        consumos=ConsumoRepositoryORM(),
        consultas_de_consumo=ConsumoQueryServiceORM(),
        recuerdos=RecuerdoQueryServiceORM(),
        compactacion=ProgramadorDeCompactacionCelery(),
        vigilante=vigilante(),  # módulo 102: el texto de los adjuntos
    )


def crear_conversacion() -> ICrearConversacionUseCase:
    return CrearConversacionUseCase(
        conversaciones=ConversacionCommandRepositoryORM(),
        carpetas=CarpetaCommandRepositoryORM(),
        uow=UnidadDeTrabajoDjango(),
    )


def modificar_conversacion() -> IModificarConversacionUseCase:
    return ModificarConversacionUseCase(
        conversaciones=ConversacionCommandRepositoryORM(),
        carpetas=CarpetaCommandRepositoryORM(),
        uow=UnidadDeTrabajoDjango(),
    )


def eliminar_conversacion() -> IEliminarConversacionUseCase:
    return EliminarConversacionUseCase(
        conversaciones=ConversacionCommandRepositoryORM(), almacen=AlmacenDjango(), uow=UnidadDeTrabajoDjango()
    )


def listar_conversaciones() -> IListarConversacionesUseCase:
    return ListarConversacionesUseCase(consultas=ConversacionQueryServiceORM())


def obtener_conversacion() -> IObtenerConversacionUseCase:
    return ObtenerConversacionUseCase(consultas=ConversacionQueryServiceORM(), almacen=AlmacenDjango())


def crear_carpeta() -> ICrearCarpetaUseCase:
    return CrearCarpetaUseCase(carpetas=CarpetaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def modificar_carpeta() -> IModificarCarpetaUseCase:  # ejercicio 1 del 97
    return ModificarCarpetaUseCase(carpetas=CarpetaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def eliminar_carpeta() -> IEliminarCarpetaUseCase:
    return EliminarCarpetaUseCase(carpetas=CarpetaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def listar_carpetas() -> IListarCarpetasUseCase:
    return ListarCarpetasUseCase(consultas=ConversacionQueryServiceORM())


def confirmar_propuesta() -> IConfirmarPropuestaUseCase:
    return ConfirmarPropuestaUseCase(
        propuestas=PropuestaCommandRepositoryORM(),
        ejecutor=EjecutorDePropuestasEnFinanzas(),
        reloj=RelojDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


def descartar_propuesta() -> IDescartarPropuestaUseCase:
    return DescartarPropuestaUseCase(propuestas=PropuestaCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def fijar_grafico() -> IFijarGraficoUseCase:
    return FijarGraficoUseCase(
        graficos=GraficoFijadoCommandRepositoryORM(),
        calculadora=_calculadora(),
        membresias=MembresiasEnHogares(),
        reloj=RelojDjango(),
        uow=UnidadDeTrabajoDjango(),
    )


def listar_graficos_fijados() -> IListarGraficosFijadosUseCase:
    return ListarGraficosFijadosUseCase(
        consultas=GraficoFijadoQueryServiceORM(),
        calculadora=_calculadora(),
        membresias=MembresiasEnHogares(),
        reloj=RelojDjango(),
    )


def quitar_grafico() -> IQuitarGraficoUseCase:
    return QuitarGraficoUseCase(graficos=GraficoFijadoCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


# ── Módulo 98: cuotas y costes ──
def consultar_cuota() -> IConsultarCuotaUseCase:
    return ConsultarCuotaUseCase(
        membresias=MembresiasEnHogares(),
        planes=PlanDelHogarRepositoryORM(),
        tarifas=TarifasDesdeAjustes(),
        consumos=ConsumoQueryServiceORM(),
        reloj=RelojDjango(),
    )


def informe_de_costes() -> IInformeDeCostesUseCase:
    return InformeDeCostesUseCase(consumos=ConsumoQueryServiceORM())


def asignar_plan() -> IAsignarPlanUseCase:
    return AsignarPlanUseCase(planes=PlanDelHogarRepositoryORM(), uow=UnidadDeTrabajoDjango())


def contar_hogares_sin_cuota() -> IContarHogaresSinCuotaUseCase:  # ejercicio 2 del 98
    return ContarHogaresSinCuotaUseCase(
        consumos=ConsumoQueryServiceORM(),
        planes=PlanDelHogarRepositoryORM(),
        tarifas=TarifasDesdeAjustes(),
        reloj=RelojDjango(),
    )


# ── Módulo 99: el contexto largo ──
def compactar_conversacion() -> ICompactarConversacionUseCase:
    return CompactarConversacionUseCase(
        conversaciones=ConversacionCommandRepositoryORM(),
        llm=llm_auxiliar(),
        consumos=ConsumoRepositoryORM(),
        tarifas=TarifasDesdeAjustes(),
        reloj=RelojDjango(),
        uow=UnidadDeTrabajoDjango(),
        umbral=settings.ASISTENTE_TOKENS_PARA_RESUMIR,
    )


def listar_recuerdos() -> IListarRecuerdosUseCase:
    return ListarRecuerdosUseCase(consultas=RecuerdoQueryServiceORM())


def olvidar_recuerdo() -> IOlvidarRecuerdoUseCase:
    return OlvidarRecuerdoUseCase(recuerdos=RecuerdoCommandRepositoryORM(), uow=UnidadDeTrabajoDjango())


def ver_contexto() -> IVerContextoUseCase:  # ejercicio 2 del 99
    return VerContextoUseCase(
        conversaciones=ConversacionCommandRepositoryORM(), recuerdos=RecuerdoQueryServiceORM(), limites=Limites()
    )


# ── Módulo 100: la ayuda (RAG) ──
def embeddings(descargar: bool = False) -> IEmbeddings | None:
    """None si no hay modelo configurado (los tests, el E2E): la búsqueda va solo por texto. Solo los comandos
    descargan el modelo (`descargar`); el chat usa el que haya en la caché, o busca por texto."""
    if not settings.ASISTENTE_EMBEDDINGS:
        return None
    return EmbeddingsFastembed(
        modelo=settings.ASISTENTE_EMBEDDINGS, cache=settings.ASISTENTE_EMBEDDINGS_CACHE, descargar=descargar
    )


def buscador_de_ayuda(llm: ILLM | None = None) -> BuscadorDeAyuda:
    return BuscadorDeAyuda(indice=IndiceDeAyudaPG(), embeddings=embeddings(), llm=llm or llm_auxiliar())


def indexar_ayuda() -> IIndexarAyudaUseCase:
    return IndexarAyudaUseCase(
        fuente=FuenteDeAyudaEnDisco(),
        indice=IndiceDeAyudaPG(),
        embeddings=embeddings(descargar=True),  # el comando del despliegue: puede (y debe) traer el modelo
        uow=UnidadDeTrabajoDjango(),
        vigilante=vigilante(),  # ejercicio 2 del 102
    )


# ── Módulo 101: text-to-SQL ──
def _text_to_sql() -> list[Tool]:
    consultas = ConsultasSQLPostgres()
    return [ConsultarSQLTool(consultas=consultas)] if settings.ASISTENTE_TEXT_TO_SQL and consultas.disponible() else []


def agente_sql() -> Agente:
    """El de la comparación (manage.py comparar_sql_y_tools): el mismo bucle y el mismo prompt, con UNA tool."""
    limites = Limites(
        segundos=settings.ASISTENTE_SEGUNDOS_POR_PREGUNTA, max_tokens=settings.ASISTENTE_TOKENS_POR_PREGUNTA
    )
    return Agente(
        llm=llm(),
        tools=[ConsultarSQLTool(consultas=ConsultasSQLPostgres())],
        limites=limites,
        telemetria=TelemetriaOTel(),
        vigilante=vigilante(),
    )


# ── Módulo 102: la seguridad ──
def vigilante() -> Vigilante | None:
    """El clasificador de inyecciones (Llama Prompt Guard 2 en Groq), con el mismo cliente que el asistente. None si
    no se configura: el resto de las defensas no dependen de él."""
    if not settings.ASISTENTE_DETECTOR_INYECCION:
        return None
    cliente = cliente_del_proceso(settings.ASISTENTE_BASE_URL, settings.ASISTENTE_API_KEY, settings.ASISTENTE_TIMEOUT)
    detector = DetectorPromptGuard(cliente=cliente, modelo=settings.ASISTENTE_DETECTOR_INYECCION)
    return Vigilante(detector, umbral=settings.ASISTENTE_UMBRAL_INYECCION, al_detectar=_contar_inyeccion)


def _contar_inyeccion(origen: str, puntuacion: float) -> None:
    """Ejercicio 1 del 102: la métrica. Por origen (pocos valores: las tools, "adjunto", "pregunta"), sin hogares."""
    instrumentos.inyecciones.add(1, {"origen": origen})


def detector_con_politica() -> DetectorConPolitica:
    """Ejercicio 3 del 102: gpt-oss-safeguard-20b con nuestra política (manage.py probar_detector --con-politica)."""
    cliente = cliente_del_proceso(settings.ASISTENTE_BASE_URL, settings.ASISTENTE_API_KEY, settings.ASISTENTE_TIMEOUT)
    return DetectorConPolitica(cliente=cliente)


# ── Módulo 103: las evals ──
def agente_para_evals(modelo: str | None = None) -> Callable[[], Agente]:
    """Un agente nuevo por caso, con las tools del chat y UN modelo: sin reserva (en una eval, el modelo que contesta
    tiene que ser el que se evalúa) y sin clasificador (se evalúa al modelo, no a las barreras: eso es el red team)."""
    llm_evaluado = llm(modelo or settings.ASISTENTE_MODELO)
    return lambda: Agente(llm=llm_evaluado, tools=tools(chat=True), telemetria=TelemetriaOTel())
