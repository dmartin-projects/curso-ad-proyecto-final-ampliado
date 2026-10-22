from django.apps import AppConfig


class OauthConfig(AppConfig):
    name = "oauth"
    verbose_name = "OAuth 2.1 y OpenID Connect"

    def ready(self):
        # La extensión de drf-spectacular que documenta el security scheme oauth2 se registra al importarla
        from .infrastructure.api.schema import esquema_oauth  # noqa: F401
