# usuarios/domain/read_models/sesion_activa.py — una sesión abierta, en la pantalla «Sesiones» (módulo 92)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class SesionActiva:
    sid: str
    canal: str  # "spa" o "autorizacion" (las páginas donde se da acceso a otras aplicaciones)
    dispositivo: str  # "Chrome en macOS"
    ip: str  # aproximada
    creada: datetime
    ultimo_uso: datetime
    factores: tuple[str, ...]
    actual: bool  # es la de esta petición
