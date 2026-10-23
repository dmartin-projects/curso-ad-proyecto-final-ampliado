# usuarios/domain/events/seguridad_cambiada_event.py — (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class SeguridadCambiadaEvent:
    """Un cambio en la forma de entrar (el MFA activado o desactivado, una passkey más o menos) o una señal de que
    alguien lo está intentando (fallos seguidos del segundo factor, un refresh token reutilizado), y la recuperación
    de la cuenta."""

    usuario_id: int
    cambio: str  # "mfa_activado", "passkey_registrada", "fallos_segundo_factor", "contrasena_recuperada"…
    detalle: str = ""  # el nombre de la passkey, el dispositivo de la sesión cerrada
