# notificaciones/infrastructure/database/repositories/destinatarios_orm.py — IDestinatarios: los usuarios y las membresías, leídos con el ORM (módulo 88)
from django.contrib.auth import get_user_model

from hogares.models import Membresia as MembresiaModel
from notificaciones.application.ports.i_destinatarios import IDestinatarios


class DestinatariosORM(IDestinatarios):
    """Lectura entre apps: los usuarios (y sus idiomas) y las membresías."""

    def idiomas(self, usuario_ids):
        usuarios = get_user_model().objects.filter(pk__in=usuario_ids).order_by("pk")
        return dict(usuarios.values_list("pk", "idioma"))

    def miembros_activos(self, hogar_id):
        return list(
            get_user_model().objects.filter(membresias__hogar_id=hogar_id, is_active=True).values_list("pk", flat=True)
        )

    def hogares(self, usuario_id):
        return list(MembresiaModel.objects.filter(usuario_id=usuario_id).values_list("hogar_id", flat=True))
