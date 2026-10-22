# backoffice/infrastructure/api/permissions/permisos_por_accion.py — los permisos de Django de cada acción (módulos 79 y 88)
from rest_framework.permissions import BasePermission


class PermisosPorAccion(BasePermission):
    """Permisos de modelo de Django (los del grupo Soporte, módulo 14) por acción de la vista.

    Cierra por defecto: una acción que no aparezca en `permisos_por_accion` no se puede usar.
    """

    message = "Tu usuario de personal no tiene permiso para esta acción."

    def has_permission(self, request, view):
        requeridos = getattr(view, "permisos_por_accion", {}).get(getattr(view, "action", None))
        if requeridos is None:
            return False
        return request.user.has_perms(requeridos)
