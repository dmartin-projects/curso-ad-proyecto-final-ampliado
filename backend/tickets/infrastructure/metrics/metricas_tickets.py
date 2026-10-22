# tickets/infrastructure/metrics/metricas_tickets.py — los tickets atascados como métrica (ejercicio 2 del
# módulo 84; módulo 88)
#
# Hasta el módulo 84 solo se veían si alguien abría la pantalla de soporte (módulo 79). Como métrica, Grafana
# puede avisar cuando aparecen, aunque nadie esté mirando.

from django.db import connection
from opentelemetry import metrics
from opentelemetry.metrics import Observation

from tickets.application.contar_tickets_atascados_use_case.dtos.contar_tickets_atascados_input_dto import (
    ContarTicketsAtascadosInputDTO,
)
from tickets.infrastructure import container


def contar_atascados() -> int:
    # El mismo criterio que la pantalla de soporte (15 min, ATASCADO): la regla es de los tickets (domain)
    return container.contar_tickets_atascados().ejecutar(ContarTicketsAtascadosInputDTO())


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
