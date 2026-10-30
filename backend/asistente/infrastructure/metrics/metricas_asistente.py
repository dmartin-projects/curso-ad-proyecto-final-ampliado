# asistente/infrastructure/metrics/metricas_asistente.py — los hogares sin cuota, como métrica (98, ejercicio 2)
#
# Como los tickets atascados (módulo 84): un gauge observable que se LEE al exportar, con el mismo valor en todos los
# procesos (en Grafana, max()).

from django.db import connection
from opentelemetry import metrics
from opentelemetry.metrics import Observation

from asistente.application.contar_hogares_sin_cuota_use_case.dtos.contar_hogares_sin_cuota_input_dto import (
    ContarHogaresSinCuotaInputDTO,
)
from asistente.infrastructure import container


def _observar(_opciones):
    try:
        yield Observation(container.contar_hogares_sin_cuota().ejecutar(ContarHogaresSinCuotaInputDTO()))
    except Exception:  # sin base de datos no hay dato: un hueco, no un cero falso
        return
    finally:
        if not connection.in_atomic_block:  # el hilo del SDK no pasa por el ciclo de una petición
            connection.close()


def _disponible(_opciones):
    """Ejercicio 3 del 107: 1 si se puede preguntar; 0 si no, con el motivo (apagado o sin_modelos). Solo Redis y los
    ajustes: barato de leer cada vez que se exporta."""
    try:
        estado = container.estado_del_asistente().estado()
    except Exception:  # sin Redis no se sabe: un hueco
        return
    yield Observation(1 if estado.activo else 0, {"motivo": estado.motivo or "activo"})


def registrar() -> None:
    metrics.get_meter("gastos.asistente").create_observable_gauge(
        "gastos.asistente.hogares_sin_cuota",
        callbacks=[_observar],
        unit="{hogar}",
        description="Hogares que ya han gastado la cuota del mes de su plan",
    )
    metrics.get_meter("gastos.asistente").create_observable_gauge(
        "gastos.asistente.disponible",
        callbacks=[_disponible],
        unit="1",
        description="1 si el asistente contesta; 0 si está apagado o sin ningún modelo disponible (ejercicio 3 del 107)",
    )
