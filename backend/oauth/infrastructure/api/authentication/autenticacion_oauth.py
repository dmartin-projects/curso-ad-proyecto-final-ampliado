# oauth/infrastructure/api/authentication/autenticacion_oauth.py — la API de Gastos como resource server (módulo 90)
#
# Es lo que las APIs de las demás apps usan (contrato de import-linter), siempre a través de AceptaOAuth: una view
# acepta tokens de aplicaciones solo si lo dice (`AceptaOAuth` y sus `scopes_por_accion`). Las demás (cuenta,
# contraseñas, backoffice) ni los miran: un token OAuth allí es un Bearer que JWTAuthentication no entiende → 401.
from django.contrib.auth.models import AnonymousUser
from oauth2_provider.oauth2_backends import get_oauthlib_core
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from core.domain.vo.delegacion import Delegacion
from oauth.domain.services.scopes import techo
from oauth.infrastructure.api.authentication.token_no_valido_exception import TokenNoValidoException
from oauth.infrastructure.server.generadores_de_tokens import PREFIJO_ACCESS


class AutenticacionOAuth(BaseAuthentication):
    """Un access token de Gastos (`Authorization: Bearer gst_at_…`): opaco, se busca en la base de datos.

    Devuelve (usuario, Delegacion). Un token de un servicio (client credentials) no tiene usuario: AnonymousUser, y
    las views de los usuarios lo rechazan (IsAuthenticated) con un 403.
    """

    def authenticate(self, request):
        partes = get_authorization_header(request).split()
        if len(partes) != 2 or partes[0].lower() != b"bearer" or not partes[1].startswith(PREFIJO_ACCESS.encode()):
            return None  # no es nuestro: que lo intente la siguiente (el JWT de la SPA)
        valido, r = get_oauthlib_core().verify_request(request, scopes=[])  # existe, no caducado, no revocado
        if not valido:
            raise TokenNoValidoException()
        token = r.access_token
        if token.user is not None and not token.user.is_active:
            raise TokenNoValidoException()
        scopes = frozenset(token.scope.split())
        delegacion = Delegacion(cliente_id=token.application.client_id, scopes=scopes, techo=techo(scopes))
        return (token.user or AnonymousUser(), delegacion)

    def authenticate_header(self, request):
        # RFC 6750 §3: el 401 dice al cliente qué ha fallado (DRF usa el del primer authenticator de la view)
        return 'Bearer realm="api", error="invalid_token"' if _bearer_nuestro(request) else 'Bearer realm="api"'


def _bearer_nuestro(request) -> bool:
    return PREFIJO_ACCESS.encode() in get_authorization_header(request)
