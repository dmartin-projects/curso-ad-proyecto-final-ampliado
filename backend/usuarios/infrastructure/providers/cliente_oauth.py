# usuarios/infrastructure/providers/cliente_oauth.py — lo común a los proveedores: el canje del code (módulo 91)
#
# Gastos es un CONFIDENTIAL client (patrón BFF): el code se canjea desde el servidor, con el client secret, y los
# tokens del proveedor se quedan aquí: sirven para saber quién es la persona y se descartan al terminar la petición.
#
# Authlib, a nivel de protocolo (rfc6749, rfc7636, oidc.core), con el httpx del proyecto: sus integraciones de cliente
# HTTP (OAuth2Client) son para requests o para httpx2, y Gastos usa httpx (y respx en los tests) desde el módulo 74.
import logging

import httpx
from authlib.oauth2.auth import ClientAuth
from authlib.oauth2.rfc6749.parameters import prepare_grant_uri, prepare_token_request
from authlib.oauth2.rfc7636 import create_s256_code_challenge

from usuarios.application.ports.i_proveedor_identidad import IProveedorIdentidad
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.vo.transaccion_social import TransaccionSocial

logger = logging.getLogger(__name__)
TIMEOUT = httpx.Timeout(10.0)


class ClienteOAuth(IProveedorIdentidad):
    """Un cliente OAuth 2.0 de un proveedor: arma la URL de autorización y canjea el code."""

    proveedor: Proveedor
    scope: str
    autenticacion = "client_secret_basic"  # cómo se autentica Gastos en el token endpoint (RFC 6749 §2.3.1)
    modo_respuesta: str | None = None  # cómo vuelve el navegador: en la query (None) o con un POST ("form_post")
    reautentica = False  # módulo 92, ej. 3: OAuth 2.0 a secas no dice cuándo se autenticó la persona

    def __init__(self, *, client_id: str, client_secret: str = "", vuelta: str):
        self.client_id, self.client_secret, self.vuelta = client_id, client_secret, vuelta

    def _url(self, endpoint: str, transaccion: TransaccionSocial, *, pkce: bool, **extra) -> str:
        if pkce:  # S256: el challenge viaja por el navegador; el verifier, solo en el canje
            extra |= {"code_challenge": create_s256_code_challenge(transaccion.code_verifier)}
            extra |= {"code_challenge_method": "S256"}
        return prepare_grant_uri(endpoint, self.client_id, "code", self.vuelta, self.scope, transaccion.state, **extra)

    def _secreto(self) -> str:
        return self.client_secret

    def _canjear(self, token_endpoint: str, code: str | None, code_verifier: str | None) -> dict:
        """POST al token endpoint (back channel). Errores del proveedor (que GitHub da con un 200) → LoginSocialNoValidoException."""
        if not code:
            raise LoginSocialNoValidoException()
        # la MISMA redirect_uri que en la ida; el verifier, solo si se mandó su challenge
        cuerpo = prepare_token_request(
            "authorization_code", code=code, redirect_uri=self.vuelta, code_verifier=code_verifier
        )
        cabeceras = {"Content-Type": "application/x-www-form-urlencoded", "Accept": "application/json"}
        url, cabeceras, cuerpo = ClientAuth(self.client_id, self._secreto(), self.autenticacion).prepare(
            "POST", token_endpoint, cabeceras, cuerpo
        )
        datos = self._json("POST", url, headers=cabeceras, content=cuerpo, aceptar_error=True)
        if "error" in datos or "access_token" not in datos:
            logger.warning("%s rechaza el code: %s", self.proveedor, datos.get("error", "sin access_token"))
            raise LoginSocialNoValidoException()
        return datos

    def _json(self, metodo: str, url: str, *, aceptar_error: bool = False, **kwargs):
        """Una petición al proveedor. Si no contesta o contesta algo que no es JSON: LoginSocialNoValidoException (y al log)."""
        try:
            with httpx.Client(timeout=TIMEOUT) as http:
                respuesta = http.request(metodo, url, **kwargs)
            if not aceptar_error:
                respuesta.raise_for_status()
            return respuesta.json()
        except (httpx.HTTPError, ValueError) as e:
            logger.warning("%s: %s %s falló: %s", self.proveedor, metodo, url, e)
            raise LoginSocialNoValidoException() from e
