# usuarios/domain/enums/estado_cuenta.py — el estado de una cuenta de usuario (módulos 35 y 88)
from enum import StrEnum


class EstadoCuenta(StrEnum):
    """En qué punto está una cuenta: decide qué correo recibe quien se registra o pide una contraseña nueva."""

    PENDIENTE = "pendiente"  # registrada, sin contraseña todavía: le falta completar el registro
    ACTIVA = "activa"
    DESACTIVADA = "desactivada"  # por soporte: ni el registro ni la recuperación la reactivan

    @classmethod
    def de(cls, *, activa: bool, con_contrasena: bool) -> "EstadoCuenta":
        if activa:
            return cls.ACTIVA
        return cls.DESACTIVADA if con_contrasena else cls.PENDIENTE
