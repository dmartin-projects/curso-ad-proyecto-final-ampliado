# notificaciones/application/obtener_notificacion_use_case/i_obtener_notificacion_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from notificaciones.application.obtener_notificacion_use_case.dtos.obtener_notificacion_input_dto import (
    ObtenerNotificacionInputDTO,
)
from notificaciones.application.shared.dtos.notificacion_listada_output_dto import NotificacionListadaOutputDTO


class IObtenerNotificacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerNotificacionInputDTO) -> NotificacionListadaOutputDTO | None: ...
