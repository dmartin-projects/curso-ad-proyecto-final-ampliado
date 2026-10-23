"""Un autenticador WebAuthn en software, para los tests (módulo 92): lo que haría la huella del móvil o una llave USB.

Genera respuestas de verdad (CBOR, COSE, ECDSA P-256), las mismas que el navegador entrega con credential.toJSON(),
para que py_webauthn las compruebe como en producción. Los tests negativos cambian una pieza cada vez: el origen, el
rp_id, el reto, la firma, el contador, los flags.
"""

import base64
import hashlib
import json
import secrets
from dataclasses import dataclass, field

import cbor2
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec

UP, UV, BE, BS, AT = 0x01, 0x04, 0x08, 0x10, 0x40  # los flags de authenticatorData


def b64(datos: bytes) -> str:
    return base64.urlsafe_b64encode(datos).rstrip(b"=").decode()


def de_b64(texto: str) -> bytes:
    return base64.urlsafe_b64decode(texto + "=" * (-len(texto) % 4))


@dataclass
class Credencial:
    id: bytes
    clave: ec.EllipticCurvePrivateKey
    rp_id: str
    manija: bytes
    contador: int = 0


@dataclass
class AutenticadorFalso:
    origen: str = "http://localhost:4200"
    verifica_usuario: bool = True  # tiene huella o PIN
    sincroniza: bool = False  # sus passkeys se copian a la nube (BE y BS)
    cuenta_firmas: bool = True  # lleva signCount (las sincronizadas suelen dar siempre 0)
    credenciales: list[Credencial] = field(default_factory=list)

    def _flags(self, *, registro: bool) -> int:
        flags = UP | (UV if self.verifica_usuario else 0) | ((BE | BS) if self.sincroniza else 0)
        return flags | (AT if registro else 0)

    @staticmethod
    def _cliente(tipo: str, opciones: dict, origen: str) -> bytes:
        return json.dumps(
            {"type": tipo, "challenge": opciones["challenge"], "origin": origen, "crossOrigin": False}
        ).encode()

    def crear(self, opciones: dict, *, origen: str | None = None, rp_id: str | None = None) -> dict:
        """navigator.credentials.create() con las opciones de Gastos (el JSON de opciones_de_registro)."""
        rp_id = rp_id or opciones["rp"]["id"]
        clave = ec.generate_private_key(ec.SECP256R1())
        numeros = clave.public_key().public_numbers()
        cose = cbor2.dumps({1: 2, 3: -7, -1: 1, -2: numeros.x.to_bytes(32, "big"), -3: numeros.y.to_bytes(32, "big")})
        credencial = Credencial(secrets.token_bytes(16), clave, rp_id, de_b64(opciones["user"]["id"]))
        self.credenciales.append(credencial)
        datos = (
            hashlib.sha256(rp_id.encode()).digest() + bytes([self._flags(registro=True)]) + (0).to_bytes(4, "big")
            + bytes(16) + len(credencial.id).to_bytes(2, "big") + credencial.id + cose
        )  # fmt: skip
        atestacion = cbor2.dumps({"fmt": "none", "attStmt": {}, "authData": datos})
        return {
            "id": b64(credencial.id), "rawId": b64(credencial.id), "type": "public-key",
            "authenticatorAttachment": "platform", "clientExtensionResults": {},
            "response": {
                "clientDataJSON": b64(self._cliente("webauthn.create", opciones, origen or self.origen)),
                "attestationObject": b64(atestacion), "transports": ["internal", "hybrid"],
            },
        }  # fmt: skip

    def firmar(
        self,
        opciones: dict,
        *,
        credencial: Credencial | None = None,
        origen: str | None = None,
        contador: int | None = None,
        manija: bytes | None = None,
    ) -> dict:
        """navigator.credentials.get(): la primera credencial permitida (o la que se diga), firmando el reto."""
        permitidas = {de_b64(c["id"]) for c in opciones.get("allowCredentials") or []}
        credencial = credencial or next(c for c in self.credenciales if not permitidas or c.id in permitidas)
        if self.cuenta_firmas:
            credencial.contador += 1
        firma_n = credencial.contador if contador is None else contador
        datos = (
            hashlib.sha256(credencial.rp_id.encode()).digest() + bytes([self._flags(registro=False)])
            + (firma_n if self.cuenta_firmas or contador is not None else 0).to_bytes(4, "big")
        )  # fmt: skip
        cliente = self._cliente("webauthn.get", opciones, origen or self.origen)
        firma = credencial.clave.sign(datos + hashlib.sha256(cliente).digest(), ec.ECDSA(hashes.SHA256()))
        return {
            "id": b64(credencial.id), "rawId": b64(credencial.id), "type": "public-key",
            "authenticatorAttachment": "platform", "clientExtensionResults": {},
            "response": {
                "clientDataJSON": b64(cliente), "authenticatorData": b64(datos), "signature": b64(firma),
                "userHandle": b64(credencial.manija if manija is None else manija),
            },
        }  # fmt: skip
