# oauth/infrastructure/api/permissions/es_servicio.py — solo un servicio: client credentials (módulo 90)
from rest_framework.permissions import BasePermission

from core.domain.vo.delegacion import Delegacion


class EsServicio(BasePermission):
    """Solo un token de servicio (client credentials): una Delegacion sin usuario."""

    def has_permission(self, request, view):
        return isinstance(request.auth, Delegacion) and not request.user.is_authenticated
