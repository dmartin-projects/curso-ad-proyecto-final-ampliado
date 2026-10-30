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


def registrar() -> None:
    metrics.get_meter("gastos.asistente").create_observable_gauge(
        "gastos.asistente.hogares_sin_cuota",
        callbacks=[_observar],
        unit="{hogar}",
        description="Hogares que ya han gastado la cuota del mes de su plan",
    )
