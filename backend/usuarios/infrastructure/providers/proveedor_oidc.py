# usuarios/infrastructure/providers/proveedor_oidc.py — un OpenID Provider cualquiera (Google, Apple…) (módulo 91)
#
# Del emisor (issuer) sale todo: el discovery da los endpoints, si admite PKCE y dónde está su JWKS. El ID token se
# valida entero (OIDC Core §3.1.3.7): algoritmo de una lista blanca, firma con la clave del JWKS por `kid`, iss, aud,
# exp/iat y nonce. Lo que no valida la librería si no se lo pides (aud), se le pide.
from authlib.oidc.core import CodeIDToken
from django.core.cache import cache
from joserfc import jwt
from joserfc.errors import InvalidKeyIdError, JoseError
from joserfc.jwk import KeySet

from usuarios.domain.exceptions.login_social_no_valido_exception import LoginSocialNoValidoException
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.domain.vo.transaccion_social import TransaccionSocial
from usuarios.infrastructure.providers.cliente_oauth import ClienteOAuth, logger

UNA_HORA = 3600
MARGEN_DE_RELOJ = 30  # segundos de tolerancia con el reloj del proveedor (exp, iat)


def es_cierto(valor) -> bool:
    """`email_verified`: un booleano en Google; en Apple, el booleano o el texto "true"."""
    return valor is True or valor == "true"


class ProveedorOIDC(ClienteOAuth):
    scope = "openid email profile"
    algoritmos = ("RS256",)  # lista blanca: nunca "none", nunca HS256 con la clave pública (confusión de algoritmos)
    parametros_extra: dict[str, str] = {}  # los propios de cada proveedor en la URL de autorización

    def __init__(self, *, emisor: str, **kwargs):
        super().__init__(**kwargs)
        self.emisor = emisor

    def emisores(self) -> list[str]:
        """Los `iss` que se aceptan en un ID token: el emisor, exacto."""
        return [self.emisor]

    # Ejercicio 1: tres puntos de extensión para un emisor que no es una URL fija (Microsoft, multi-tenant)
    def issuer_del_discovery(self) -> str:
        return self.emisor

    def iss_valido(self, iss: str, claims: dict) -> bool:
        """El `iss` del ID token (con sus claims al lado)."""
        return iss in self.emisores()

    def iss_de_respuesta_valido(self, iss: str) -> bool:
        """El `iss` de la vuelta (RFC 9207), antes de canjear el code: todavía no hay ID token."""
        return iss in self.emisores()

    # ── El discovery y el JWKS, una hora en la caché (como un navegador con Cache-Control) ──

    def _metadatos(self) -> dict:
        clave = f"social:discovery:{self.emisor}"
        if (metadatos := cache.get(clave)) is None:
            metadatos = self._json("GET", f"{self.emisor}/.well-known/openid-configuration")
            if metadatos.get("issuer") != self.issuer_del_discovery():  # los endpoints de OTRO emisor: no se usa
                logger.warning("%s: el discovery dice issuer=%r", self.proveedor, metadatos.get("issuer"))
                raise LoginSocialNoValidoException()
            cache.set(clave, metadatos, UNA_HORA)
        return metadatos

    def _jwks(self, *, de_nuevo: bool = False) -> KeySet:
        clave = f"social:jwks:{self.emisor}"
        if de_nuevo or (jwks := cache.get(clave)) is None:
            jwks = self._json("GET", self._metadatos()["jwks_uri"])
            cache.set(clave, jwks, UNA_HORA)
        return KeySet.import_key_set(jwks)

    def _pkce(self) -> bool:
        """PKCE si el proveedor lo anuncia (Google sí; Apple no lo anuncia: ahí protegen el `nonce` y el secreto)."""
        return "S256" in self._metadatos().get("code_challenge_methods_supported", [])

    # ── El flujo ──

    def url_de_autorizacion(self, transaccion: TransaccionSocial) -> str:
        extra = {"nonce": transaccion.nonce, "response_mode": self.modo_respuesta, **self.parametros_extra}
        return self._url(self._metadatos()["authorization_endpoint"], transaccion, pkce=self._pkce(), **extra)

    def completar(self, transaccion: TransaccionSocial, parametros: dict[str, str]) -> PerfilExterno:
        # RFC 9207: si el proveedor dice quién responde, tiene que ser él (mix-up). Además, cada proveedor tiene su
        # propia redirect URI y la transacción recuerda a cuál se fue: la respuesta de uno no se canjea en otro
        iss = parametros.get("iss")
        if iss is not None and not self.iss_de_respuesta_valido(iss):
            raise LoginSocialNoValidoException()
        verifier = transaccion.code_verifier if self._pkce() else None
        tokens = self._canjear(self._metadatos()["token_endpoint"], parametros.get("code"), verifier)
        claims = self.validar_id_token(tokens.get("id_token"), transaccion.nonce, tokens["access_token"])
        if iss is not None and iss != claims["iss"]:  # y el que firma el ID token es el mismo que ha respondido
            raise LoginSocialNoValidoException()
        return self._perfil(claims, parametros)

    def validar_id_token(self, id_token: str | None, nonce: str, access_token: str | None = None) -> dict:
        if not id_token:
            raise LoginSocialNoValidoException()
        try:
            try:
                token = jwt.decode(id_token, self._jwks(), algorithms=list(self.algoritmos))
            except InvalidKeyIdError:  # un `kid` que no está: quizá ha rotado la clave. Se vuelve a pedir, UNA vez
                token = jwt.decode(id_token, self._jwks(de_nuevo=True), algorithms=list(self.algoritmos))
            claims = CodeIDToken(
                token.claims,
                token.header,
                # CodeIDToken exige que estén iss, sub, aud, exp e iat, y comprueba exp e iat; los VALORES de iss y aud
                # solo si se le dan: se le dan los dos (iss, con una función: ejercicio 1)
                options={
                    "iss": {"essential": True, "validate": lambda claims, iss: self.iss_valido(iss, claims)},
                    "aud": {"essential": True, "value": self.client_id},
                },
                # Y con estos, nonce (si se pasa, el del token tiene que ser ese), azp y at_hash
                params={"nonce": nonce, "client_id": self.client_id, "access_token": access_token},
            )
            claims.validate(leeway=MARGEN_DE_RELOJ)
        except (JoseError, ValueError) as e:
            logger.warning("%s: ID token no válido: %s", self.proveedor, e)
            raise LoginSocialNoValidoException() from e
        return dict(claims)

    def _perfil(self, claims: dict, parametros: dict[str, str]) -> PerfilExterno:
        return PerfilExterno(
            proveedor=self.proveedor,
            sub=claims["sub"],
            email=claims.get("email"),
            email_verificado=es_cierto(claims.get("email_verified")),
            nombre=claims.get("given_name", ""),
            apellidos=claims.get("family_name", ""),
        )
