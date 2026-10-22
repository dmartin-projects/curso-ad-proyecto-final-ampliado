# oauth/infrastructure/server/scopes_por_cliente.py — cada cliente, solo sus scopes (SCOPES_BACKEND_CLASS, módulo 90)
from oauth2_provider.scopes import SettingsScopes
from oauth2_provider.settings import oauth2_settings

from oauth.infrastructure.database.models.cliente_oauth_model import ClienteOAuth as ClienteOAuthModel


class ScopesPorCliente(SettingsScopes):
    """DOT, por defecto, deja a cualquier cliente pedir cualquier scope de SCOPES. Aquí, solo los suyos."""

    def get_available_scopes(self, application=None, request=None, *args, **kwargs):
        if application is None:  # el documento de discovery: todos los que existen
            return list(oauth2_settings._SCOPES)
        permitidos = ClienteOAuthModel.objects.filter(aplicacion=application).values_list("scopes", flat=True).first()
        return list(permitidos or [])  # una Application sin ClienteOAuth no puede pedir nada

    def get_default_scopes(self, application=None, request=None, *args, **kwargs):
        return []  # sin scopes por defecto: el cliente dice lo que quiere (y el usuario lo ve)
