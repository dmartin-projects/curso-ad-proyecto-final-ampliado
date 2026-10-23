# usuarios/infrastructure/mfa/totp_pyotp.py — ITotp con pyotp (RFC 6238) (módulo 92)
#
# TOTP (RFC 6238) = HOTP (RFC 4226) con el contador sustituido por el tiempo: el paso es floor(unix_time / 30) y el
# código, los 6 últimos dígitos de un HMAC-SHA1(secreto, paso). La app del móvil y Gastos comparten el secreto y el
# reloj; ninguno manda nada al otro.
import hmac

import pyotp

from usuarios.application.ports.i_totp import ITotp


class TotpPyotp(ITotp):
    def nuevo_secreto(self) -> str:
        return pyotp.random_base32()  # 32 caracteres base32 = 160 bits (lo que recomienda el RFC 4226)

    def paso(self, secreto, codigo, ahora):
        """`pyotp.TOTP.verify(codigo, valid_window=1)` hace esto mismo, pero solo dice sí o no. Gastos necesita SABER
        qué paso ha valido: es lo que se guarda para no aceptar el mismo código otra vez (ni uno anterior)."""
        if len(codigo) != 6 or not codigo.isdigit():
            return None
        totp = pyotp.TOTP(secreto)
        actual = totp.timecode(ahora)
        # ±1 paso (±30 s): el reloj del móvil no va a la par y la persona tarda en teclear. Más ventana, más códigos
        # válidos a la vez para quien prueba a ciegas (3 de cada millón con ±1)
        for paso in (actual - 1, actual, actual + 1):
            if hmac.compare_digest(totp.generate_otp(paso), codigo):  # en tiempo constante
                return paso
        return None

    def uri(self, secreto, cuenta):
        return pyotp.TOTP(secreto).provisioning_uri(name=cuenta, issuer_name="Gastos")
