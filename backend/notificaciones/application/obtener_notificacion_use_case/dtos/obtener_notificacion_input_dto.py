# notificaciones/application/obtener_notificacion_use_case/dtos/obtener_notificacion_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerNotificacionInputDTO:
    usuario_id: int
    notificacion_id: int
