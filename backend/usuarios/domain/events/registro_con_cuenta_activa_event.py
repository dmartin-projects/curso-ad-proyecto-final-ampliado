# usuarios/domain/events/registro_con_cuenta_activa_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class RegistroConCuentaActivaEvent:
    usuario_id: int
    enlace: str  # → el email "Ya tienes una cuenta", con el enlace para elegir otra contraseña
