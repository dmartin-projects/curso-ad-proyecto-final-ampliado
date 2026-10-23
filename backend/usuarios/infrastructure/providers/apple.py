# usuarios/infrastructure/providers/apple.py — Sign in with Apple, en la web (módulo 91)
#
# OpenID Connect con tres particularidades:
# - La vuelta es un POST (response_mode=form_post): Apple lo exige si se piden name o email.
# - El client secret no es un texto fijo: es un JWT que firma Gastos (ES256) con la clave .p8 de su cuenta de Apple.
# - El nombre solo llega la PRIMERA vez, y fuera del ID token (el campo `user` del POST, sin firmar). El email puede
#   ser una dirección de relay (…@privaterelay.appleid.com) y `email_verified` puede ser el texto "true".
import json
import time

from joserfc import jwt
from joserfc.jwk import ECKey

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.infrastructure.providers.proveedor_oidc import ProveedorOIDC, es_cierto

VIDA_DEL_SECRETO = 300  # segundos. Apple admite hasta seis meses; uno nuevo en cada canje no hay que guardarlo


class Apple(ProveedorOIDC):
    proveedor = Proveedor.APPLE
    scope = (
        "openid name email"  # su documentación habla de name y email; openid lo exige OIDC y su discovery lo anuncia
    )
    modo_respuesta = "form_post"
    autenticacion = "client_secret_post"  # el único que anuncia su discovery
    # Módulo 92, ejercicio 3: su petición de autorización no recoge max_age ni prompt: no se puede forzar que vuelva a
    # pedir la contraseña, así que no se ofrece para el step-up
    reautentica = False

    def __init__(self, *, equipo: str, clave_id: str, clave_privada: str, **kwargs):
        super().__init__(**kwargs)  # client_id = el Services ID (com.tudominio.gastos.web)
        self.equipo, self.clave_id, self.clave_privada = equipo, clave_id, clave_privada

    def _secreto(self) -> str:
        ahora = int(time.time())
        return jwt.encode(
            {"alg": "ES256", "kid": self.clave_id},
            {
                "iss": self.equipo,
                "iat": ahora,
                "exp": ahora + VIDA_DEL_SECRETO,
                "aud": self.emisor,
                "sub": self.client_id,
            },
            ECKey.import_key(self.clave_privada),
        )

    def _perfil(self, claims: dict, parametros: dict[str, str]) -> PerfilExterno:
        nombre = _nombre(parametros.get("user"))  # solo la primera vez; sin firmar: solo para el nombre
        return PerfilExterno(
            proveedor=self.proveedor,
            sub=claims["sub"],
            email=claims.get("email"),  # el del ID token (firmado), nunca el de `user`
            email_verificado=es_cierto(claims.get("email_verified")),
            nombre=nombre.get("firstName", ""),
            apellidos=nombre.get("lastName", ""),
        )


def _nombre(user: str | None) -> dict:
    try:
        nombre = json.loads(user or "{}").get("name") or {}
    except (ValueError, AttributeError):
        return {}
    return {k: v for k, v in nombre.items() if isinstance(v, str)} if isinstance(nombre, dict) else {}
