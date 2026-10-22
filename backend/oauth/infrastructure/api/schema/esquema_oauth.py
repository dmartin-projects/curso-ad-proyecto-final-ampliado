# oauth/infrastructure/api/schema/esquema_oauth.py — el security scheme oauth2 en OpenAPI (módulo 90)
#
# drf-spectacular registra la extensión al importar este módulo: lo importa OauthConfig.ready() (apps.py).
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from oauth2_provider.settings import oauth2_settings

from oauth.infrastructure.api.authentication.autenticacion_oauth import AutenticacionOAuth


class EsquemaOAuth(OpenApiAuthenticationExtension):
    """OpenAPI: el security scheme oauth2 (con sus flujos y scopes) y, en cada operación, el scope que pide."""

    target_class = AutenticacionOAuth
    name = "oauth2"

    def get_security_definition(self, auto_schema):
        scopes = {s: str(d) for s, d in oauth2_settings.SCOPES.items()}
        return {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": "/api/oauth/authorize/",
                    "tokenUrl": "/api/oauth/token/",
                    "refreshUrl": "/api/oauth/token/",
                    "scopes": scopes,
                },
                "clientCredentials": {"tokenUrl": "/api/oauth/token/", "scopes": scopes},
            },
        }

    def get_security_requirement(self, auto_schema):
        scope = getattr(auto_schema.view, "scopes_por_accion", {}).get(getattr(auto_schema.view, "action", None))
        return {self.name: [scope]} if scope else None
