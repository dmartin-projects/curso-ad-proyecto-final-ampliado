# notificaciones/domain/read_models/notificacion_listada.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class NotificacionListada:
    id: int
    tipo: str
    titulo: str
    mensaje: str
    enlace: str
    hogar_id: int | None
    datos: dict
    leida: bool
    creado: datetime
