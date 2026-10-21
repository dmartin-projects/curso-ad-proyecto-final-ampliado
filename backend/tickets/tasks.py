import logging

from celery import Task, shared_task
from opentelemetry import metrics

from core.circuito import CircuitoAbierto

from . import services
from .ia import ErrorRespuestaIA, ErrorTransitorioIA
from .models import Ticket

logger = logging.getLogger(__name__)

# Módulo 84: una métrica de NEGOCIO. Las automáticas dicen cuánto tarda la web; esta, cuántos tickets
# terminan bien, en revisión o con error. En Prometheus: gastos_tickets_procesados_total{estado="…"}
procesados = metrics.get_meter("gastos.tickets").create_counter(
    "gastos.tickets.procesados", unit="{ticket}", description="Tickets que terminan de procesarse, por estado"
)
# Las tres series a 0 desde el arranque del proceso: increase() no ve el salto "no existía → 1", y el PRIMER
# ticket de cada proceso no contaría (el panel marcaría uno menos por cada proceso arrancado)
for _estado in (Ticket.Estado.PROCESADO, Ticket.Estado.REVISAR, Ticket.Estado.ERROR):
    procesados.add(0, {"estado": _estado})


class TareaTicket(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Fallo definitivo (sin más reintentos o error no previsto): el ticket queda en `error`."""
        logger.warning("Ticket %s fallido: %r", args[0], exc)
        services.marcar_error(args[0], f"{exc.__class__.__name__}: {exc}")
        procesados.add(1, {"estado": Ticket.Estado.ERROR})


@shared_task(
    base=TareaTicket,
    bind=True,
    acks_late=True,  # si el worker muere a mitad, RabbitMQ entrega el mensaje a otro (por eso es idempotente)
    autoretry_for=(ErrorTransitorioIA, CircuitoAbierto),
    retry_backoff=30,  # 30 s, 60 s, 120 s… (con jitter) hasta retry_backoff_max
    retry_backoff_max=900,
    retry_jitter=True,
    max_retries=5,
    rate_limit="30/m",  # por worker: no saturar la cuota del proveedor de IA
)
def procesar_ticket(self, ticket_id: int) -> str:
    ticket = services.empezar(ticket_id)
    if ticket is None:
        return "omitido"
    try:
        ticket = services.procesar(ticket)
    except ErrorRespuestaIA as e:
        # la IA ha respondido algo inservible: reintentar no lo arreglará → el usuario lo completa a mano
        services.marcar_error(ticket_id, str(e), estado=Ticket.Estado.REVISAR)
        procesados.add(1, {"estado": Ticket.Estado.REVISAR})
        return Ticket.Estado.REVISAR
    procesados.add(1, {"estado": ticket.estado})
    logger.info("Ticket %s terminado: %s", ticket_id, ticket.estado)  # dentro de la traza: Loki ↔ Tempo
    return ticket.estado
