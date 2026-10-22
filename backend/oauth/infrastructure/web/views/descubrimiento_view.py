# oauth/infrastructure/web/views/descubrimiento_view.py — /.well-known/openid-configuration (módulo 90)
import json

from oauth2_provider.views import ConnectDiscoveryInfoView


class DescubrimientoView(ConnectDiscoveryInfoView):
    """/.well-known/openid-configuration de django-oauth-toolkit, con dos retoques:

    - Solo RS256: DOT anuncia también HS256, y Gastos firma todos sus ID tokens con RS256. Anunciar lo que no se usa
      invita a un cliente a aceptarlo.
    - El revocation_endpoint (RFC 7009, un metadato del RFC 8414 que OIDC Discovery admite): sin él, un cliente no
      sabe dónde revocar sus tokens al cerrar sesión.
    """

    def get(self, request, *args, **kwargs):
        respuesta = super().get(request, *args, **kwargs)
        datos = json.loads(respuesta.content)
        datos["id_token_signing_alg_values_supported"] = ["RS256"]
        datos["revocation_endpoint"] = self._get_endpoint_url(request, "revoke-token", required=True)
        respuesta.content = json.dumps(datos)
        return respuesta
