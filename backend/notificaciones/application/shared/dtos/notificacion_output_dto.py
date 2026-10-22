# notificaciones/application/shared/dtos/notificacion_output_dto.py (módulo 88)
from dataclasses import dataclass

from notificaciones.domain.bo.notificacion import Notificacion


@dataclass(frozen=True, slots=True)
class NotificacionOutputDTO:
    id: int
    usuario_id: int
    tipo: str
    titulo: str
    mensaje: str
    hogar_id: int | None
    enlace: str
    datos: dict

    @classmethod
    def desde_bo(cls, n: Notificacion) -> "NotificacionOutputDTO":
        return cls(n.id, n.usuario_id, str(n.tipo), n.titulo, n.mensaje, n.hogar_id, n.enlace, dict(n.datos))
