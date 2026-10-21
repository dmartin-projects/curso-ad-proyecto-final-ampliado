"""Módulo 84, ejercicio 2: los tickets atascados como métrica, para poder avisar de ellos.

Hasta ahora solo se veían si alguien abría la pantalla de soporte (módulo 79). Como métrica, Grafana
puede avisar cuando aparecen, aunque nadie esté mirando.
"""

from django.db import connection
from django.db.models import Q
from django.utils import timezone
from opentelemetry import metrics
from opentelemetry.metrics import Observation

from .models import ATASCADO, Ticket  # el mismo criterio que la pantalla de soporte: 15 min


def contar_atascados() -> int:
    limite = timezone.now() - ATASCADO
    return Ticket.objects.filter(
        Q(estado__in=[Ticket.Estado.PENDIENTE, Ticket.Estado.PROCESANDO]), actualizado__lt=limite
    ).count()


def _observar(_opciones):
    """La llama el SDK al exportar (cada 60 s), en SU hilo, no en el de una petición."""
    try:
        yield Observation(contar_atascados())
    except Exception:  # sin base de datos no hay dato: mejor un hueco en la gráfica que un valor falso
        return
    finally:
        # Ese hilo no pasa por el ciclo petición/respuesta de Django, que es quien cierra las conexiones:
        # sin esto, cada proceso dejaría una conexión abierta para siempre. (En los tests se lee la
        # métrica dentro de la transacción del test: ahí no se puede cerrar.)
        if not connection.in_atomic_block:
            connection.close()


def registrar() -> None:
    # Un gauge "observable": no se actualiza en el código, se LEE cuando toca exportar. Cada proceso con
    # OpenTelemetry lo exporta (web, workers…), con el mismo valor: en Grafana se usa max(), no sum()
    metrics.get_meter("gastos.tickets").create_observable_gauge(
        "gastos.tickets.atascados",
        callbacks=[_observar],
        unit="{ticket}",
        description="Tickets pendientes o procesando sin cambios desde hace más de 15 minutos",
    )
