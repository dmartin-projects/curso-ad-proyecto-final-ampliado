# oauth/infrastructure/api/permissions/scope_requerido.py — el scope que pide cada acción (módulo 90)
from rest_framework.permissions import BasePermission

from core.domain.vo.delegacion import Delegacion
from oauth.infrastructure.api.permissions.scope_insuficiente_exception import ScopeInsuficienteException


class ScopeRequerido(BasePermission):
    """Con un token OAuth, la acción tiene que estar en `scopes_por_accion` y el token, tener ese scope. Lo que no
    aparece no se delega (cerrado por defecto). Sin token OAuth (la SPA, con su JWT), no hay nada que mirar."""

    def has_permission(self, request, view):
        if not isinstance(request.auth, Delegacion):
            return True
        requerido = getattr(view, "scopes_por_accion", {}).get(getattr(view, "action", None))
        if requerido is None or not request.auth.permite(requerido):
            raise ScopeInsuficienteException(requerido)
        return True
