# hogares/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de los hogares (módulos 72, 76, 85 y 88)
#
# Los cambios de membresía los publica el use case y aquí se traducen: el outbox (Kafka), en la misma transacción;
# el aviso a los sockets, al confirmar.
from django.db import transaction
from django.utils.module_loading import import_string

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from eventos.application.ports.i_outbox import IOutbox
from hogares.domain.events.hogar_creado_event import HogarCreadoEvent
from hogares.domain.events.invitacion_enviada_event import InvitacionEnviadaEvent
from hogares.domain.events.miembro_anadido_event import MiembroAnadidoEvent
from hogares.domain.events.miembro_expulsado_event import MiembroExpulsadoEvent
from hogares.domain.events.rol_cambiado_event import RolCambiadoEvent
from hogares.infrastructure.database.models.hogar_model import Hogar as HogarModel
from hogares.infrastructure.signals import hogares_signals

ENVIAR_INVITACION = "hogares.tasks.enviar_invitacion"  # su ruta estable (core/infrastructure/tasks/ruta_estable.py)


def _grupos_cambiados(usuario_id: int) -> None:
    transaction.on_commit(lambda: hogares_signals.miembros_cambiados.send(sender=HogarModel, usuario_id=usuario_id))


class PublicadorEventosDjango(IPublicadorEventos):
    def __init__(self, *, outbox: IOutbox):
        self.outbox = outbox

    def publicar(self, *eventos: object) -> None:
        for evento in eventos:
            match evento:
                case HogarCreadoEvent(hogar_id=hogar_id):
                    hogares_signals.hogar_creado.send(sender=HogarModel, hogar_id=hogar_id)  # ya, en esta transacción
                case MiembroAnadidoEvent(hogar_id=h, usuario_id=u, rol=rol):
                    self.outbox.membresia_guardada(h, u, rol)
                    _grupos_cambiados(u)
                case RolCambiadoEvent(hogar_id=h, usuario_id=u, rol=rol):
                    self.outbox.membresia_guardada(h, u, rol)  # el rol decide qué estadísticas puede ver
                case MiembroExpulsadoEvent(hogar_id=h, usuario_id=u):
                    self.outbox.membresia_borrada(h, u)
                    _grupos_cambiados(u)
                case InvitacionEnviadaEvent(invitacion_id=pk):
                    # La tarea por su ruta, como la busca el worker: el publicador no importa tasks/, que está por
                    # encima en las capas (como las de Celery por su nombre)
                    transaction.on_commit(lambda pk=pk: import_string(ENVIAR_INVITACION).enqueue(pk))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
