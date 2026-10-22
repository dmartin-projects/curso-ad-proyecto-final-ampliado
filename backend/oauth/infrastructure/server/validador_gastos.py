# oauth/infrastructure/server/validador_gastos.py — las reglas de Gastos dentro de oauthlib (OAUTH2_VALIDATOR_CLASS, módulo 90)
from oauth2_provider.oauth2_validators import OAuth2Validator


class ValidadorGastos(OAuth2Validator):
    def validate_scopes(self, client_id, scopes, client, request, *args, **kwargs):
        # Sin `scope` no hay token (RFC 6749 §3.3 permite fallar con invalid_scope): un token "para nada" no sirve
        return bool(scopes) and super().validate_scopes(client_id, scopes, client, request, *args, **kwargs)

    def validate_refresh_token(self, refresh_token, client, request, *args, **kwargs):
        valido = super().validate_refresh_token(refresh_token, client, request, *args, **kwargs)
        return valido and request.user.is_active  # una cuenta desactivada ya no renueva tokens

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
