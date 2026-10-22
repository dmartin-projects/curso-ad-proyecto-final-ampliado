# notificaciones/infrastructure/database/services/marcar_leidas.py — marcar como leídas (módulo 88)
#
# Marcar como leída no tiene reglas ni efectos (solo las tuyas: lo hace el filtro): CRUD, sin use case (módulo 87).
from django.utils import timezone

from notificaciones.infrastructure.database.models.notificacion_model import Notificacion as NotificacionModel


def marcar_leidas(usuario_id: int, ids=None) -> int:
    qs = NotificacionModel.objects.filter(usuario_id=usuario_id, leida=False)
    if ids is not None:
        qs = qs.filter(pk__in=ids)
    return qs.update(leida=True, leida_en=timezone.now())
