# usuarios/domain/vo/factores_disponibles.py — con qué puede completar el segundo paso una cuenta (módulo 92)
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FactoresDisponibles:
    """Con qué puede completar el segundo paso (o un step-up) esta cuenta."""

    totp: bool = False
    passkeys: bool = False
    recuperacion: bool = False
    contrasena: bool = False  # solo para el step-up de una cuenta sin MFA
    proveedores: list[str] = field(default_factory=list)  # ídem, sin contraseña: volver a entrar con el proveedor

    def lista(self) -> list[str]:
        nombres = {"totp": self.totp, "passkey": self.passkeys, "recuperacion": self.recuperacion,
                   "contrasena": self.contrasena}  # fmt: skip
        return [n for n, si in nombres.items() if si]

    def segundos(self) -> list[str]:
        """Los que completan el segundo paso del login."""
        return [n for n in self.lista() if n != "contrasena"]
