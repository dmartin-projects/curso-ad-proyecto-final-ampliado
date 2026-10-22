# estadisticas/infrastructure/container.py — composition root del servicio de estadísticas (módulo 89)
#
# El ÚNICO sitio que sabe qué implementación va detrás de cada interfaz y de dónde sale cada cosa (configuración,
# sesiones, reloj). Una función por use case, como en el monolito (módulo 87), con la interfaz como tipo de
# retorno. La usan los tres adapters de entrada:
#
# - la API, con Depends: `Depends(container.obtener_tendencia)`. Las funciones de los use cases de consulta piden a
#   su vez su Session y su reloj con Depends, así que FastAPI monta el use case de cada petición (y en un test se
#   cambia una pieza con app.dependency_overrides[container.reloj]);
# - el consumidor de Kafka, que pide container.procesar_lote() al arrancar;
# - el comando de reconstruir, que pide container.reconstruir_proyeccion().
#
# Funciones y no un framework de DI: montar un use case cuesta microsegundos y se lee de un vistazo. En un test con
# base de datos, una pieza se cambia con monkeypatch.setattr(container, "MovimientoCommandRepositorySQL", …).
from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from estadisticas.ajustes import ajustes
from estadisticas.application.obtener_dias_semana_use_case.i_obtener_dias_semana_use_case import (
    IObtenerDiasSemanaUseCase,
)
from estadisticas.application.obtener_dias_semana_use_case.obtener_dias_semana_use_case import (
    ObtenerDiasSemanaUseCase,
)
from estadisticas.application.obtener_sin_revisar_use_case.i_obtener_sin_revisar_use_case import (
    IObtenerSinRevisarUseCase,
)
from estadisticas.application.obtener_sin_revisar_use_case.obtener_sin_revisar_use_case import (
    ObtenerSinRevisarUseCase,
)
from estadisticas.application.obtener_tendencia_use_case.i_obtener_tendencia_use_case import IObtenerTendenciaUseCase
from estadisticas.application.obtener_tendencia_use_case.obtener_tendencia_use_case import ObtenerTendenciaUseCase
from estadisticas.application.ports.i_reloj import IReloj
from estadisticas.application.procesar_lote_use_case.i_procesar_lote_use_case import IProcesarLoteUseCase
from estadisticas.application.procesar_lote_use_case.procesar_lote_use_case import ProcesarLoteUseCase
from estadisticas.application.reconstruir_proyeccion_use_case.i_reconstruir_proyeccion_use_case import (
    IReconstruirProyeccionUseCase,
)
from estadisticas.application.reconstruir_proyeccion_use_case.reconstruir_proyeccion_use_case import (
    ReconstruirProyeccionUseCase,
)
from estadisticas.domain.enums.topic import Topic
from estadisticas.domain.repositories.i_membresia_query_service import IMembresiaQueryService
from estadisticas.domain.repositories.i_progreso_query_service import IProgresoQueryService
from estadisticas.infrastructure.clock.reloj_sistema import RelojSistema
from estadisticas.infrastructure.database import sesiones
from estadisticas.infrastructure.database.repositories.membresia_command_repository_sql import (
    MembresiaCommandRepositorySQL,
)
from estadisticas.infrastructure.database.repositories.membresia_query_service_sql import MembresiaQueryServiceSQL
from estadisticas.infrastructure.database.repositories.movimiento_command_repository_sql import (
    MovimientoCommandRepositorySQL,
)
from estadisticas.infrastructure.database.repositories.movimiento_query_service_sql import MovimientoQueryServiceSQL
from estadisticas.infrastructure.database.repositories.progreso_command_repository_sql import (
    ProgresoCommandRepositorySQL,
)
from estadisticas.infrastructure.database.repositories.progreso_query_service_sql import ProgresoQueryServiceSQL
from estadisticas.infrastructure.database.unidad_de_trabajo_sql import UnidadDeTrabajoSQL
from estadisticas.infrastructure.messaging.aparcados_kafka import AparcadosKafka
from estadisticas.infrastructure.messaging.grupo_kafka import GrupoKafka
from estadisticas.infrastructure.telemetry.trazas_otel import TrazasOTel


# ── Lo que viene de fuera (dependencias de FastAPI) ──
def sesion() -> Iterator[Session]:
    """Una sesión por petición, para los query services (solo leen)."""
    with sesiones.sesion() as s:
        yield s


Sesion = Annotated[Session, Depends(sesion)]


def reloj() -> IReloj:
    return RelojSistema()


Reloj = Annotated[IReloj, Depends(reloj)]


def clave_jwt() -> str:
    return ajustes().jwt_signing_key


# ── Query services que usa la API fuera de un use case (el permiso por hogar y la salud) ──
def membresia_query_service(s: Sesion) -> IMembresiaQueryService:
    return MembresiaQueryServiceSQL(s)


def progreso_query_service(s: Sesion) -> IProgresoQueryService:
    return ProgresoQueryServiceSQL(s)


# ── Los use cases de consulta (la API) ──
def obtener_tendencia(s: Sesion, r: Reloj) -> IObtenerTendenciaUseCase:
    return ObtenerTendenciaUseCase(
        movimientos=MovimientoQueryServiceSQL(s), progreso=ProgresoQueryServiceSQL(s), reloj=r
    )


def obtener_dias_semana(s: Sesion, r: Reloj) -> IObtenerDiasSemanaUseCase:
    return ObtenerDiasSemanaUseCase(
        movimientos=MovimientoQueryServiceSQL(s), progreso=ProgresoQueryServiceSQL(s), reloj=r
    )


def obtener_sin_revisar(s: Sesion, r: Reloj) -> IObtenerSinRevisarUseCase:
    return ObtenerSinRevisarUseCase(
        movimientos=MovimientoQueryServiceSQL(s), progreso=ProgresoQueryServiceSQL(s), reloj=r
    )


# ── Los use cases de comando (el consumidor y los comandos) ──
def procesar_lote() -> IProcesarLoteUseCase:
    a = ajustes()
    s = sesiones.sesion()  # una Session para la unidad de trabajo y los repositorios: la misma transacción
    return ProcesarLoteUseCase(
        uow=UnidadDeTrabajoSQL(s),
        movimientos=MovimientoCommandRepositorySQL(s),
        membresias=MembresiaCommandRepositorySQL(s),
        progreso=ProgresoCommandRepositorySQL(s),
        aparcados=AparcadosKafka(a.kafka_bootstrap_servers, a.topic_dlq),
        trazas=TrazasOTel(),
        topics={a.topic_movimientos: Topic.MOVIMIENTOS, a.topic_membresias: Topic.MEMBRESIAS},
    )


def reconstruir_proyeccion() -> IReconstruirProyeccionUseCase:
    a = ajustes()
    s = sesiones.sesion()
    return ReconstruirProyeccionUseCase(
        grupo=GrupoKafka(a.kafka_bootstrap_servers, a.kafka_grupo),
        uow=UnidadDeTrabajoSQL(s),
        movimientos=MovimientoCommandRepositorySQL(s),
        membresias=MembresiaCommandRepositorySQL(s),
        progreso=ProgresoCommandRepositorySQL(s),
    )
