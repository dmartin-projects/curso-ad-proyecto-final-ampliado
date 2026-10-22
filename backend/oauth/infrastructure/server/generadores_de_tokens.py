# oauth/infrastructure/server/generadores_de_tokens.py — los tokens que emite el servidor: opacos y con prefijo (módulo 90)
#
# django-oauth-toolkit (DOT) implementa los endpoints (authorize, token, revoke, userinfo, discovery, JWKS) sobre
# oauthlib. Lo que es de Gastos se enchufa en sus ajustes (OAUTH2_PROVIDER en config/settings/base.py), y vive en
# esta carpeta:
#   SCOPES_BACKEND_CLASS    ScopesPorCliente: cada cliente, solo los scopes con los que se registró.
#   OAUTH2_VALIDATOR_CLASS  ValidadorGastos: sin scopes por defecto, cuentas desactivadas fuera, claims del usuario.
#   ACCESS/REFRESH_TOKEN_GENERATOR  tokens opacos con prefijo (gst_at_, gst_rt_): este archivo.
import secrets

# Un prefijo dice qué es un token sin consultar nada: los escáneres de secretos (GitHub secret scanning, gitleaks) lo
# reconocen si se filtra en un repositorio o un log, y la API sabe a qué autenticación pasárselo
# (api/authentication/autenticacion_oauth.py).
PREFIJO_ACCESS, PREFIJO_REFRESH = "gst_at_", "gst_rt_"


def generar_access_token(request) -> str:
    return PREFIJO_ACCESS + secrets.token_urlsafe(32)  # 256 bits aleatorios: no se puede adivinar


def generar_refresh_token(request) -> str:
    return PREFIJO_REFRESH + secrets.token_urlsafe(32)
