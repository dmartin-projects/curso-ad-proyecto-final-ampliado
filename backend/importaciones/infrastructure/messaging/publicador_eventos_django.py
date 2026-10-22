# importaciones/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de las importaciones (módulos 75, 84 y 88)
#
# Los use cases publican hechos y aquí se decide qué significan: la tarea que se encola, el chord de los lotes, el
# aviso a las notificaciones, las métricas. Todo on_commit.
from celery import chord, current_app
from django.conf import settings
from django.db import transaction
from opentelemetry import metrics

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from importaciones.domain.enums.estado_importacion import EstadoImportacion
from importaciones.domain.enums.formato import Formato
from importaciones.domain.events.extracto_subido_event import ExtractoSubidoEvent
from importaciones.domain.events.importacion_analizada_event import ImportacionAnalizadaEvent
from importaciones.domain.events.importacion_confirmada_event import ImportacionConfirmadaEvent
from importaciones.domain.events.importacion_terminada_event import ImportacionTerminadaEvent
from importaciones.domain.events.lote_importado_event import LoteImportadoEvent
from importaciones.infrastructure.database.models.importacion_model import Importacion as ImportacionModel
from importaciones.infrastructure.signals import importaciones_signals as signals

# Las tareas, por su nombre (el de name=): el publicador no importa tasks/, que está por encima en las capas
ANALIZAR, LOTE = "importaciones.tasks.analizar_importacion", "importaciones.tasks.importar_lote"
FINALIZAR, FALLIDA = "importaciones.tasks.finalizar_importacion", "importaciones.tasks.importacion_fallida"

# Módulo 84, ejercicio 1: métricas de negocio de las importaciones. En Prometheus:
#   gastos_importaciones_total{formato="csv",estado="completada"}  y  gastos_importaciones_movimientos_total
_medidor = metrics.get_meter("gastos.importaciones")
importaciones = _medidor.create_counter(
    "gastos.importaciones", unit="{importacion}", description="Importaciones terminadas, por formato y estado"
)
movimientos_creados = _medidor.create_counter(
    "gastos.importaciones.movimientos", unit="{movimiento}", description="Movimientos nuevos creados al importar"
)
# Todas las series, a 0 desde el arranque: increase() de Prometheus no puede contar el salto "no existía → 1",
# y sin esto la PRIMERA importación de cada proceso no aparecería en el panel (marcaría 0)
for _formato in Formato:
    movimientos_creados.add(0, {"formato": _formato})
    for _estado in (EstadoImportacion.COMPLETADA, EstadoImportacion.ERROR):
        importaciones.add(0, {"formato": _formato, "estado": _estado})


def _tarea(nombre: str):
    return current_app.tasks[nombre]


def _avisar(senal, importacion_id: int) -> None:
    senal.send(
        sender=ImportacionModel,
        importacion=ImportacionModel.objects.select_related("hogar", "subido_por").get(pk=importacion_id),
    )


def _lanzar(importacion_id: int, filas: tuple[int, ...]) -> None:
    """Chord (módulo 26): los lotes en paralelo en todos los workers y, cuando terminan TODOS, el cierre."""
    tam = settings.IMPORTACION_TAMANO_LOTE
    lotes = [list(filas[i : i + tam]) for i in range(0, len(filas), tam)]
    if not lotes:
        _tarea(FINALIZAR).delay(importacion_id)
        return
    cierre = _tarea(FINALIZAR).si(importacion_id).on_error(_tarea(FALLIDA).si(importacion_id))
    chord(_tarea(LOTE).si(importacion_id, lote) for lote in lotes)(cierre)


def _terminada(e: ImportacionTerminadaEvent) -> None:
    estado = EstadoImportacion.COMPLETADA if e.completada else EstadoImportacion.ERROR
    importaciones.add(1, {"formato": e.formato, "estado": estado})
    if e.completada:
        movimientos_creados.add(e.creados, {"formato": e.formato})
    _avisar(signals.importacion_terminada, e.importacion_id)


class PublicadorEventosDjango(IPublicadorEventos):
    def publicar(self, *eventos: object) -> None:
        for evento in eventos:
            match evento:
                case ExtractoSubidoEvent(importacion_id=pk):
                    transaction.on_commit(lambda pk=pk: _tarea(ANALIZAR).delay(pk))
                case ImportacionAnalizadaEvent(importacion_id=pk):
                    transaction.on_commit(lambda pk=pk: _avisar(signals.importacion_analizada, pk))
                case ImportacionConfirmadaEvent(importacion_id=pk, filas=filas):
                    transaction.on_commit(lambda pk=pk, filas=filas: _lanzar(pk, filas))
                case LoteImportadoEvent(importacion_id=pk):
                    transaction.on_commit(lambda pk=pk: _avisar(signals.importacion_progreso, pk))
                case ImportacionTerminadaEvent():
                    transaction.on_commit(lambda e=evento: _terminada(e))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
