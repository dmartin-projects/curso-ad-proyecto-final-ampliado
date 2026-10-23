# usuarios/infrastructure/providers/github.py — Sign in with GitHub: OAuth 2.0 sin OpenID Connect (módulo 91)
#
# GitHub no emite ID tokens: no hay nada firmado que diga quién es la persona. Gastos obtiene un access token y
# PREGUNTA a su API: /user (el id) y /user/emails (si el email está verificado). La identidad es el `id` numérico,
# nunca el `login`: un usuario puede cambiar de nombre y otro quedarse el antiguo.
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial
from usuarios.infrastructure.providers.cliente_oauth import ClienteOAuth

CABECERAS_API = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}


class GitHub(ClienteOAuth):
    proveedor = Proveedor.GITHUB
    scope = "read:user user:email"  # en una GitHub App, el permiso de cuenta «Email addresses» (lectura)
    autenticacion = "client_secret_post"

    def __init__(self, *, web: str, api: str, **kwargs):
        super().__init__(**kwargs)
        self.web, self.api = web, api  # https://github.com, https://api.github.com (en los tests, otros)

    def url_de_autorizacion(self, transaccion: TransaccionSocial) -> str:
        # PKCE (S256) desde julio de 2025. Sin nonce: no hay ID token en el que volver a encontrarlo
        return self._url(f"{self.web}/login/oauth/authorize", transaccion, pkce=True)

    def completar(self, transaccion: TransaccionSocial, parametros: dict[str, str]) -> PerfilExterno:
        tokens = self._canjear(
            f"{self.web}/login/oauth/access_token", parametros.get("code"), transaccion.code_verifier
        )
        cabeceras = CABECERAS_API | {"Authorization": f"Bearer {tokens['access_token']}"}
        usuario = self._json("GET", f"{self.api}/user", headers=cabeceras)
        correos = self._json("GET", f"{self.api}/user/emails", headers=cabeceras)
        if not isinstance(usuario, dict) or not isinstance(usuario.get("id"), int) or not isinstance(correos, list):
            raise LoginSocialNoValidoException()
        # El principal, si está verificado. Uno sin verificar puede ser de cualquiera (GitHub deja añadirlo)
        principal = next((c for c in correos if isinstance(c, dict) and c.get("primary")), {})
        return PerfilExterno(
            proveedor=self.proveedor,
            sub=str(usuario["id"]),
            email=principal.get("email"),
            email_verificado=principal.get("verified") is True,
            nombre=usuario.get("name") or usuario.get("login") or "",
        )
