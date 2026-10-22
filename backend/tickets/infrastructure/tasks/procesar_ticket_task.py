# tickets/infrastructure/tasks/procesar_ticket_task.py — adapter de entrada de Celery (módulos 26, 74, 84 y 88)
import logging

from celery import Task, shared_task
from opentelemetry import metrics

from core.infrastructure.cache.circuito_abierto_exception import CircuitoAbiertoException
from tickets.application.procesar_ticket_use_case.dtos.procesar_ticket_input_dto import ProcesarTicketInputDTO
from tickets.application.terminar_sin_gasto_use_case.dtos.terminar_sin_gasto_input_dto import TerminarSinGastoInputDTO
from tickets.domain.enums.estado_ticket import EstadoTicket
from tickets.infrastructure import container
from tickets.infrastructure.ia.transitorio_ia_exception import TransitorioIAException
from tickets.infrastructure.messaging.publicador_eventos_django import PROCESAR_TICKET

logger = logging.getLogger(__name__)

# Módulo 84: una métrica de NEGOCIO. Las automáticas dicen cuánto tarda la web; esta, cuántos tickets
# terminan bien, en revisión o con error. En Prometheus: gastos_tickets_procesados_total{estado="…"}
procesados = metrics.get_meter("gastos.tickets").create_counter(
    "gastos.tickets.procesados", unit="{ticket}", description="Tickets que terminan de procesarse, por estado"
)
# Las tres series a 0 desde el arranque del proceso: increase() no ve el salto "no existía → 1", y el PRIMER
# ticket de cada proceso no contaría (el panel marcaría uno menos por cada proceso arrancado)
for _estado in (EstadoTicket.PROCESADO, EstadoTicket.REVISAR, EstadoTicket.ERROR):
    procesados.add(0, {"estado": _estado})


class TareaTicket(Task):
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Fallo definitivo (sin más reintentos o error no previsto): el ticket queda en `error`."""
        logger.warning("Ticket %s fallido: %r", args[0], exc)
        container.terminar_sin_gasto().ejecutar(TerminarSinGastoInputDTO(args[0], f"{exc.__class__.__name__}: {exc}"))
        procesados.add(1, {"estado": EstadoTicket.ERROR})


# name= explícito (módulo 87): el nombre de siempre. Además de los mensajes ya encolados, de él depende la COLA:
# CELERY_TASK_ROUTES manda "tickets.tasks.*" a la cola "ocr", la de los workers con Tesseract.
@shared_task(
    name=PROCESAR_TICKET,
    base=TareaTicket,
    bind=True,
    acks_late=True,  # si el worker muere a mitad, RabbitMQ entrega el mensaje a otro (por eso es idempotente)
    autoretry_for=(TransitorioIAException, CircuitoAbiertoException),
    retry_backoff=30,  # 30 s, 60 s, 120 s… (con jitter) hasta retry_backoff_max
    retry_backoff_max=900,
    retry_jitter=True,
    max_retries=5,
    rate_limit="30/m",  # por worker: no saturar la cuota del proveedor de IA
)
def procesar_ticket(self, ticket_id: int) -> str:
    estado = container.procesar_ticket().ejecutar(ProcesarTicketInputDTO(ticket_id))
    if estado is None:
        return "omitido"
    procesados.add(1, {"estado": estado})
    logger.info("Ticket %s terminado: %s", ticket_id, estado)  # dentro de la traza: Loki ↔ Tempo
    return estado
