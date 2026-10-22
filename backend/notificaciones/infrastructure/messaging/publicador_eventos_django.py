# notificaciones/infrastructure/messaging/publicador_eventos_django.py — IPublicadorEventos de las notificaciones (módulos 76 y 88)
from django.db import transaction
from django.utils.module_loading import import_string

from core.application.ports.i_publicador_eventos import IPublicadorEventos
from notificaciones.domain.events.notificaciones_creadas_event import NotificacionesCreadasEvent
from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel
from notificaciones.infrastructure.realtime.tiempo_real import datos_ws, emitir_a_usuario

ENVIAR_EMAIL = "notificaciones.tasks.enviar_email_notificacion"  # su ruta estable (django.tasks)


def _al_confirmar(ids: tuple[int, ...], email: bool) -> None:
    for n in NotificacionModel.objects.filter(pk__in=ids).order_by("pk"):
        emitir_a_usuario(n.usuario_id, "notificacion.nueva", datos_ws(n))
        if email:
            import_string(ENVIAR_EMAIL).enqueue(n.pk)


class PublicadorEventosDjango(IPublicadorEventos):
    def publicar(self, *eventos: object) -> None:
        for evento in eventos:
            match evento:
                case NotificacionesCreadasEvent(ids=ids, email=email):
                    transaction.on_commit(lambda ids=ids, email=email: _al_confirmar(ids, email))
                case _:
                    raise TypeError(f"Evento sin traducción: {evento!r}")
