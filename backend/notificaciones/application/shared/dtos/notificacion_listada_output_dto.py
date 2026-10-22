# notificaciones/application/shared/dtos/notificacion_listada_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from notificaciones.domain.read_models.notificacion_listada import NotificacionListada


@dataclass(frozen=True, slots=True)
class NotificacionListadaOutputDTO:
    id: int
    tipo: str
    titulo: str
    mensaje: str
    enlace: str
    hogar_id: int | None
    datos: dict
    leida: bool
    creado: datetime

    @classmethod
    def desde_read_model(cls, rm: NotificacionListada) -> "NotificacionListadaOutputDTO":
        return cls(**{campo: getattr(rm, campo) for campo in cls.__dataclass_fields__})
