# oauth/infrastructure/api/permissions/scope_insuficiente_exception.py — 403 de un token sin el scope (módulo 90)
from rest_framework import exceptions


class ScopeInsuficienteException(exceptions.PermissionDenied):
    """403 con el WWW-Authenticate del RFC 6750 §3.1: el cliente sabe qué scope tiene que pedir."""

    def __init__(self, scope: str | None):
        if scope:
            super().__init__(f"Este token no tiene el scope «{scope}».")
            self.auth_header = f'Bearer realm="api", error="insufficient_scope", scope="{scope}"'
        else:
            super().__init__("Esta acción no se puede hacer con el token de una aplicación.")
            self.auth_header = 'Bearer realm="api", error="insufficient_scope"'
