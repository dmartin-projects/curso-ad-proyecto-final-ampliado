# usuarios/domain/events/inicio_desde_dispositivo_nuevo_event.py — (módulo 92)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class InicioDesdeDispositivoNuevoEvent:
    usuario_id: int
    dispositivo: str  # "Chrome en macOS"
    ip: str  # aproximada: "83.45.120.0/24"
    momento: datetime
