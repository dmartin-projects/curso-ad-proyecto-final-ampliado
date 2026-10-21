"""Módulo 85, ejercicio 1: el outbox atascado como métrica, para que Grafana avise.

Si el relay se para (o Kafka no responde), Django sigue funcionando y los eventos se acumulan en silencio.
La proyección se queda atrás y nadie lo nota hasta que alguien mira las estadísticas. Con estas dos
métricas, Grafana avisa en minutos.

Se exportan desde TODOS los procesos (no solo desde el relay): si el relay está caído, es justo cuando
más falta hace el dato. En Grafana, max() y no sum().
"""

from django.db import connection
from django.db.models import Count, Min
from django.utils import timezone
from opentelemetry import metrics
from opentelemetry.instrumentation.utils import suppress_instrumentation
from opentelemetry.metrics import Observation

from .models import EventoPendiente


def estado_outbox() -> tuple[int, float]:
    """(cuántos eventos sin publicar, segundos que lleva esperando el más antiguo)."""
    datos = EventoPendiente.objects.filter(publicado__isnull=True).aggregate(n=Count("id"), mas_antiguo=Min("creado"))
    edad = (timezone.now() - datos["mas_antiguo"]).total_seconds() if datos["mas_antiguo"] else 0.0
    return datos["n"], edad


def _observar(indice: int):
    """Callback para el SDK. Cada métrica hace su consulta (una vez por minuto: cuesta nada) en vez de
    compartir una caché, que dependería del orden en que el SDK las lee."""

    def callback(_opciones):
        try:
            with suppress_instrumentation():  # una consulta por minuto y proceso: sin traza propia en Tempo
                valor = estado_outbox()[indice]
            yield Observation(valor)
        except Exception:  # sin base de datos no hay dato: un hueco en la gráfica, no un 0 falso
            return
        finally:
            if not connection.in_atomic_block:  # mismo motivo que en tickets/metricas.py (módulo 84)
                with suppress_instrumentation():
                    connection.close()

    return callback


def registrar() -> None:
    medidor = metrics.get_meter("gastos.eventos")
    medidor.create_observable_gauge(
        "gastos.eventos.pendientes",
        callbacks=[_observar(0)],
        unit="{evento}",
        description="Eventos del outbox que aún no se han publicado en Kafka",
    )
    medidor.create_observable_gauge(
        "gastos.eventos.antiguedad",
        callbacks=[_observar(1)],
        unit="s",
        description="Segundos que lleva esperando el evento sin publicar más antiguo (0 si no hay)",
    )
