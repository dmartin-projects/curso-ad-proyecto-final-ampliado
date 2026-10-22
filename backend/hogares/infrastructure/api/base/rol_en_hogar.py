# hogares/infrastructure/api/base/rol_en_hogar.py — el rol mínimo de cada acción, en el hogar de la URL (módulos 36, 88 y 90)
from rest_framework.permissions import BasePermission

from core.domain.enums.rol import Rol
from hogares.infrastructure.database.models.membresia_model import Membresia as MembresiaModel

ROLES_POR_METODO = {
    "GET": MembresiaModel.Rol.LECTOR,
    "HEAD": MembresiaModel.Rol.LECTOR,
    "OPTIONS": MembresiaModel.Rol.LECTOR,
    "POST": MembresiaModel.Rol.MIEMBRO,
    "PUT": MembresiaModel.Rol.MIEMBRO,
    "PATCH": MembresiaModel.Rol.MIEMBRO,
    "DELETE": MembresiaModel.Rol.MIEMBRO,
}


class RolEnHogar(BasePermission):
    """Exige un rol mínimo según el método HTTP (o según `roles_por_accion` de la vista)."""

    message = "Tu rol en este hogar no permite esta acción."

    def has_permission(self, request, view):
        if getattr(view, "swagger_fake_view", False):
            return True
        requerido = getattr(view, "roles_por_accion", {}).get(getattr(view, "action", None)) or getattr(
            view, "roles_por_metodo", ROLES_POR_METODO
        ).get(request.method, MembresiaModel.Rol.ADMIN)
        return view.actor.rol.nivel >= Rol(requerido).nivel  # el rol del Actor: con un token OAuth, ya limitado
