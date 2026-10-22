# oauth/infrastructure/api/views/acepta_oauth.py — una view que acepta, ADEMÁS del JWT de la SPA, tokens OAuth (módulo 90)
from oauth.infrastructure.api.authentication.autenticacion_oauth import AutenticacionOAuth
from oauth.infrastructure.api.permissions.scope_requerido import ScopeRequerido


# Mixin para las views (ViewSet o APIView) que aceptan, ADEMÁS del JWT de la SPA, tokens de aplicaciones.
# `scopes_por_accion`: {acción: scope}; en un APIView, la acción es None. El rol en el hogar se sigue comprobando igual
# (RolEnHogar y el use case), con el Actor limitado por los scopes (actor_de, en hogares).
# (Un comentario y no un docstring: el docstring de una view, y el de sus mixins, acaba en OpenAPI.)
class AceptaOAuth:
    scopes_por_accion: dict = {}

    def get_authenticators(self):
        return [AutenticacionOAuth(), *super().get_authenticators()]  # primero: los Bearer gst_at_ son suyos

    def get_permissions(self):
        return [ScopeRequerido(), *super().get_permissions()]  # el scope, antes de mirar el hogar
