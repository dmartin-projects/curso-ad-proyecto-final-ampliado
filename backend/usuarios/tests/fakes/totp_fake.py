# usuarios/tests/fakes/totp_fake.py — ITotp en memoria (módulo 92)
from datetime import UTC, datetime

from usuarios.application.ports.i_totp import ITotp


def paso_de(momento: datetime) -> int:
    return int(momento.timestamp()) // 30


class TotpFake(ITotp):
    """El código de un paso son sus 6 últimas cifras: el test sabe cuál es el bueno sin calcular un HMAC."""

    def nuevo_secreto(self):
        return "SECRETOFALSO"

    @staticmethod
    def codigo(paso: int) -> str:
        return f"{paso % 1_000_000:06d}"

    def ahora(self) -> str:
        return self.codigo(paso_de(datetime.now(UTC)))

    def paso(self, secreto, codigo, ahora):
        actual = paso_de(ahora)
        return next((p for p in (actual - 1, actual, actual + 1) if self.codigo(p) == codigo), None)

    def uri(self, secreto, cuenta):
        return f"otpauth://totp/Gastos:{cuenta}?secret={secreto}&issuer=Gastos"
