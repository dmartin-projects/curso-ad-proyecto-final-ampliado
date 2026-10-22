# tickets/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de los tickets (módulos 74, 76 y 88)
#
# Cada use case publica un hecho y aquí se decide qué significa. Todo con on_commit: si la transacción se deshace,
# ni se encola la tarea ni se avisa; y el worker nunca lee un ticket que aún no está guardado.
from celery import current_app
from django.core.files.storage import default_storage
from django.db import transaction

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from tickets.domain.events.ticket_borrado_event import TicketBorradoEvent
from tickets.domain.events.ticket_pendiente_event import TicketPendienteEvent
from tickets.domain.events.ticket_terminado_event import TicketTerminadoEvent
from tickets.infrastructure.database.models.ticket_model import Ticket as TicketModel
from tickets.infrastructure.signals import tickets_signals

PROCESAR_TICKET = "tickets.tasks.procesar_ticket"


def _encolar(ticket_id: int) -> None:
    # La tarea, por su nombre (el de name=, módulo 87): el publicador no importa tasks/, que está por encima
    # (tasks → container → messaging)
    current_app.tasks[PROCESAR_TICKET].delay(ticket_id)


def _avisar_terminado(ticket_id: int) -> None:
    ticket = TicketModel.objects.select_related("hogar", "subido_por").get(pk=ticket_id)
    tickets_signals.ticket_terminado.send(sender=TicketModel, ticket=ticket)  # las notificaciones (módulo 76)


class PublicadorEventosDjango(IPublicadorEventos):
    def publicar(self, *eventos: object) -> None:
        for evento in eventos:
            match evento:
                case TicketPendienteEvent(ticket_id=pk):
                    transaction.on_commit(lambda pk=pk: _encolar(pk))
                case TicketTerminadoEvent(ticket_id=pk):
                    transaction.on_commit(lambda pk=pk: _avisar_terminado(pk))
                case TicketBorradoEvent(archivo=nombre):
                    transaction.on_commit(lambda nombre=nombre: default_storage.delete(nombre))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
