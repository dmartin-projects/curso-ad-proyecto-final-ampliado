"""Proveedores de identidad de mentira para los tests (módulo 91), con respx: nada sale a Internet.

`OIDCFalso` es un OpenID Provider (discovery, JWKS y token endpoint) que se comporta como Google o Apple: el ID token
que emite lleva el nonce de la petición de autorización a la que corresponde el code, y comprueba PKCE si se usó.
`GitHubFalso` es OAuth 2.0 sin OIDC: un access token y una API (/user, /user/emails).
"""

import base64
import hashlib
import secrets
import time
from urllib.parse import parse_qs, urlsplit

import httpx
from joserfc import jwt
from joserfc.jwk import KeySet, RSAKey

TOKEN_DEL_PROVEEDOR = "ya29.token-del-proveedor"  # nunca debe llegar al navegador


def _query(url: str) -> dict:
    return {k: v[0] for k, v in parse_qs(urlsplit(url).query).items()}


class OIDCFalso:
    def __init__(self, respx_mock, emisor: str, client_id: str, *, pkce=True, form_post=False):
        self.emisor, self.client_id, self.pkce = emisor, client_id, pkce
        self.clave = RSAKey.generate_key(2048, parameters={"kid": "clave-1", "use": "sig", "alg": "RS256"})
        self.claves = [self.clave]  # las publicadas en el JWKS
        self.claims = {"sub": "1081", "email": "ana@gmail.com", "email_verified": True,
                       "given_name": "Ana", "family_name": "García"}  # fmt: skip
        self.trampas: dict = {}  # claims cambiados en el ID token (iss, aud, exp…): para los tests negativos
        self.cabecera: dict = {}  # cambios en la cabecera del ID token (alg, kid)
        self.firmar_con = None  # otra clave con la que firmar (una que no está en el JWKS)
        self.pendientes: dict[str, dict] = {}  # code → la petición de autorización
        self.canjes: list[dict] = []  # lo que ha llegado al token endpoint
        metadatos = {
            "issuer": emisor,
            "authorization_endpoint": f"{emisor}/authorize",
            "token_endpoint": f"{emisor}/token",
            "jwks_uri": f"{emisor}/jwks",
            "response_types_supported": ["code"],
            "id_token_signing_alg_values_supported": ["RS256"],
        }
        if pkce:
            metadatos["code_challenge_methods_supported"] = ["S256"]
        if form_post:
            metadatos["response_modes_supported"] = ["query", "form_post"]
        self.metadatos = metadatos
        self.discovery = respx_mock.get(f"{emisor}/.well-known/openid-configuration").mock(
            side_effect=lambda r: httpx.Response(200, json=self.metadatos)
        )
        self.jwks = respx_mock.get(f"{emisor}/jwks").mock(
            side_effect=lambda r: httpx.Response(200, json=KeySet(self.claves).as_dict(private=False))
        )
        self.token = respx_mock.post(f"{emisor}/token").mock(side_effect=self._token)

    def autorizar(self, url: str, **claims) -> dict:
        """La persona entra en el proveedor y acepta: lo que vuelve al navegador (code y state). `claims`: quién es."""
        peticion = _query(url)
        assert peticion["client_id"] == self.client_id and peticion["response_type"] == "code"
        code = secrets.token_urlsafe(16)
        self.pendientes[code] = peticion | {"claims": self.claims | claims}
        return {"code": code, "state": peticion["state"]}

    def id_token(self, **claims) -> str:
        ahora = int(time.time())
        datos = {"iss": self.emisor, "aud": self.client_id, "iat": ahora, "exp": ahora + 600} | claims | self.trampas
        cabecera = {"alg": "RS256", "kid": "clave-1"} | self.cabecera
        return jwt.encode(cabecera, {k: v for k, v in datos.items() if v is not None}, self.firmar_con or self.clave)

    def _token(self, request: httpx.Request) -> httpx.Response:
        datos = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
        self.canjes.append(datos | {"_autorizacion": request.headers.get("authorization")})
        peticion = self.pendientes.pop(datos.get("code"), None)  # un code, una vez
        if peticion is None or datos.get("redirect_uri") != peticion["redirect_uri"]:
            return httpx.Response(400, json={"error": "invalid_grant"})
        if "code_challenge" in peticion:  # PKCE, como el de verdad
            hash_ = hashlib.sha256(datos.get("code_verifier", "").encode()).digest()
            if base64.urlsafe_b64encode(hash_).rstrip(b"=").decode() != peticion["code_challenge"]:
                return httpx.Response(400, json={"error": "invalid_grant"})
        id_token = self.id_token(**peticion["claims"], nonce=peticion.get("nonce"))
        return httpx.Response(
            200,
            json={
                "access_token": TOKEN_DEL_PROVEEDOR,
                "token_type": "Bearer",
                "expires_in": 3599,
                "id_token": id_token,
            },
        )


class GitHubFalso:
    def __init__(self, respx_mock, web="https://github.example", api="https://api.github.example"):
        self.usuario = {"id": 583231, "login": "ana-dev", "name": "Ana García"}
        self.correos = [
            {"email": "ana@gmail.com", "primary": True, "verified": True, "visibility": "private"},
            {"email": "ana@antiguo.example", "primary": False, "verified": False, "visibility": None},
        ]
        self.pendientes: dict[str, dict] = {}
        self.canjes: list[dict] = []
        self.token = respx_mock.post(f"{web}/login/oauth/access_token").mock(side_effect=self._token)
        self.api_usuario = respx_mock.get(f"{api}/user").mock(side_effect=lambda r: self._api(r, self.usuario))
        self.api_correos = respx_mock.get(f"{api}/user/emails").mock(side_effect=lambda r: self._api(r, self.correos))

    def autorizar(self, url: str) -> dict:
        peticion = _query(url)
        code = secrets.token_urlsafe(16)
        self.pendientes[code] = peticion
        return {"code": code, "state": peticion["state"]}

    def _token(self, request: httpx.Request) -> httpx.Response:
        datos = {k: v[0] for k, v in parse_qs(request.content.decode()).items()}
        self.canjes.append(datos)
        peticion = self.pendientes.pop(datos.get("code"), None)
        verifier_ok = peticion and base64.urlsafe_b64encode(
            hashlib.sha256(datos.get("code_verifier", "").encode()).digest()
        ).rstrip(b"=").decode() == peticion.get("code_challenge")
        if not verifier_ok:  # GitHub contesta los errores con un 200 (y "error" en el cuerpo)
            return httpx.Response(200, json={"error": "bad_verification_code"})
        return httpx.Response(200, json={"access_token": "gho_token-del-proveedor", "token_type": "bearer"})

    def _api(self, request: httpx.Request, cuerpo) -> httpx.Response:
        if request.headers.get("authorization") != "Bearer gho_token-del-proveedor":
            return httpx.Response(401, json={"message": "Bad credentials"})
        return httpx.Response(200, json=cuerpo)
