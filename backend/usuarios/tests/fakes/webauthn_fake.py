# usuarios/tests/fakes/webauthn_fake.py — IWebAuthn en memoria (módulo 92)
from usuarios.application.ports.i_webauthn import IWebAuthn
from usuarios.domain.exceptions.passkey_no_valida_exception import PasskeyNoValidaException
from usuarios.domain.vo.credencial_nueva import CredencialNueva
from usuarios.domain.vo.firma_comprobada import FirmaComprobada
from usuarios.domain.vo.reto import Reto


class WebAuthnFake(IWebAuthn):
    """Un autenticador de mentira: la "respuesta" es un dict legible. Lo que se comprueba es lo mismo que en el de
    verdad, en pequeño: el reto, la firma ("buena"), la verificación del usuario y que el contador no retroceda."""

    def __init__(self):
        self.retos = 0
        self.pedidos: list[dict] = []  # las opciones de cada ceremonia

    def _reto(self, **opciones) -> Reto:
        self.retos += 1
        self.pedidos.append(opciones)
        return Reto(opciones | {"challenge": f"reto-{self.retos}"}, f"reto-{self.retos}".encode())

    def opciones_de_registro(self, *, manija, cuenta, nombre, excluir):
        return self._reto(manija=manija, excluir=excluir)

    def comprobar_registro(self, respuesta, challenge):
        if respuesta.get("challenge", "").encode() != challenge:
            raise PasskeyNoValidaException()
        return CredencialNueva(respuesta["id"].encode(), b"clave-publica", 0, respuesta.get("sincronizada", False))

    def opciones_de_entrada(self, *, permitir, exigir_verificacion):
        return self._reto(permitir=[p.credencial_id for p in permitir], uv=exigir_verificacion)

    def credencial(self, respuesta):
        if "id" not in respuesta:
            raise PasskeyNoValidaException()
        return respuesta["id"].encode(), respuesta.get("manija")

    def comprobar_entrada(self, respuesta, challenge, passkey, *, exigir_verificacion):
        contador = respuesta.get("contador", 0)
        if (
            respuesta.get("challenge", "").encode() != challenge
            or respuesta.get("firma") != "buena"
            or (exigir_verificacion and not respuesta.get("uv"))
            or ((contador or passkey.contador) and contador <= passkey.contador)
        ):
            raise PasskeyNoValidaException()
        return FirmaComprobada(contador, passkey.sincronizada)
