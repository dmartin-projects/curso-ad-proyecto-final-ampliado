# backoffice/infrastructure/api/permissions/es_personal.py — solo personal de la empresa (módulos 79 y 88)
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission


class EsPersonal(BasePermission):
    """Solo personal de la empresa (is_staff). Un usuario normal no sabe ni que existe: 404, no 403."""

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False  # → 401
        if not request.user.is_staff:
            raise NotFound()
        return True
