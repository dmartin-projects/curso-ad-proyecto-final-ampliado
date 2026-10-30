# oauth/infrastructure/server/validador_gastos.py — las reglas de Gastos dentro de oauthlib (OAUTH2_VALIDATOR_CLASS,
# módulos 90 y 92): sin scopes por defecto, cuentas desactivadas fuera, claims del usuario y, desde el 92, amr, acr y
# auth_time de la autenticación real; desde el 104, ningún recurso (RFC 8707) que no se concediera
import hashlib
from datetime import UTC, datetime

from oauth2_provider.models import get_grant_model
from oauth2_provider.oauth2_validators import OAuth2Validator
from oauthlib.oauth2.rfc6749 import errors

from oauth.infrastructure.database.models.autenticacion_de_concesion_model import (
    AutenticacionDeConcesion as AutenticacionDeConcesionModel,
)


class ValidadorGastos(OAuth2Validator):
    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        # Sin `scope` no hay token (RFC 6749 §3.3 permite fallar con invalid_scope): un token "para nada" no sirve
        return bool(scopes) and super().validate_scopes(client_id, scopes, client, request, *args, **kwargs)

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        valido = super().validate_refresh_token(refresh_token, client, request, *args, **kwargs)
        return valido and request.user.is_active  # una cuenta desactivada ya no renueva tokens

    def _check_and_set_request_resource(self, request):
        """Módulo 104 (RFC 8707 y MCP): `resource` va en la autorización Y en el canje. DOT ya impide pedir en el canje
        (o en el refresh) un recurso distinto del concedido, pero si lo concedido no tenía recurso, acepta cualquiera:
        una app conectada para la API conseguiría tokens del servidor MCP sin que la persona viera nunca «Solo en:
        …/api/mcp» en la pantalla de consentimiento. Sin recurso concedido, pedir uno es invalid_target."""
        if request.grant_type == "authorization_code":
            concesion = get_grant_model().objects.filter(code=request.code, application=request.client).first()
            concedido = (concesion.resource or []) if concesion else []
        elif request.grant_type == "refresh_token":
            refresh = getattr(request, "refresh_token_instance", None)
            concedido = (refresh.resource or []) if refresh else []
        else:  # client credentials: no hay consentimiento de nadie (y el servidor MCP pide una persona)
            concedido = None
        super()._check_and_set_request_resource(request)
        if concedido == [] and request.resource:
            raise errors.CustomOAuth2Error(
                error="invalid_target",
                description="Ese recurso no se pidió al autorizar: la persona no lo ha consentido.",
                request=request,
            )

    def get_additional_claims(self):
        """Los claims del usuario. Cada uno sale solo con su scope (`oidc_claim_scope` de DOT: email → "email",
        name… → "profile"), en el ID token y en /userinfo. Sin el argumento `request`, DOT los anuncia además en el
        discovery (claims_supported)."""
        return {
            "email": lambda r: r.user.email,
            # Gastos activa una cuenta al confirmar su email (módulo 35): si está activa, el email es suyo
            "email_verified": lambda r: r.user.is_active,
            "name": lambda r: r.user.get_full_name(),
            "given_name": lambda r: r.user.nombre,
            "family_name": lambda r: r.user.apellidos,
            "locale": lambda r: r.user.idioma,
            "zoneinfo": lambda r: r.user.zona_horaria,
        }

    # ── Módulo 92: el ID token cuenta cómo se autenticó la persona (amr, acr) y cuándo (auth_time) ──
    # django-oauth-toolkit pone auth_time = last_login (el último login en cualquier sitio, también en la SPA) y no
    # emite amr ni acr. La autenticación real llega con el consentimiento (AutorizarView la añade a las credenciales),
    # se guarda con el code, pasa a la familia de refresh tokens al canjearlo y de ahí sale a cada ID token.

    def save_authorization_code(self, client_id, code, request, *args, **kwargs):
        super().save_authorization_code(client_id, code, request, *args, **kwargs)
        if datos := getattr(request, "autenticacion", None):
            AutenticacionDeConcesionModel.objects.create(
                codigo=_hash(code["code"]), amr=datos["amr"], acr=datos["acr"],
                auth_time=datetime.fromtimestamp(datos["auth_time"], UTC),
            )  # fmt: skip

    def validate_code(self, client_id, code, client, request, *args, **kwargs):
        valido = super().validate_code(client_id, code, client, request, *args, **kwargs)
        if valido:
            request.autenticacion = AutenticacionDeConcesionModel.objects.filter(codigo=_hash(code)).first()
        return valido

    def _create_refresh_token(self, request, refresh_token_code, access_token, previous_refresh_token):
        refresh = super()._create_refresh_token(request, refresh_token_code, access_token, previous_refresh_token)
        autenticacion = getattr(request, "autenticacion", None)
        if previous_refresh_token is None and autenticacion is not None:  # el primero de la familia: el del canje
            AutenticacionDeConcesionModel.objects.filter(pk=autenticacion.pk).update(
                codigo=None, familia=refresh.token_family
            )
        return refresh

    def get_id_token_dictionary(self, token, token_handler, request):
        claims, caduca = super().get_id_token_dictionary(token, token_handler, request)
        autenticacion = getattr(request, "autenticacion", None)
        if autenticacion is None and (refresh := getattr(request, "refresh_token_instance", None)):
            autenticacion = AutenticacionDeConcesionModel.objects.filter(familia=refresh.token_family).first()
        if autenticacion is not None:
            claims |= {
                "auth_time": int(autenticacion.auth_time.timestamp()),
                "amr": list(autenticacion.amr),
                "acr": autenticacion.acr,
            }
        return claims, caduca


def _hash(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()  # como los tokens: el code, ni siquiera mientras vive
