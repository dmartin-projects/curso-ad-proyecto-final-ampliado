# notificaciones/application/notificar_use_case/i_notificar_use_case.py (módulos 76 y 88)
from abc import ABC, abstractmethod

from notificaciones.application.notificar_use_case.dtos.notificar_input_dto import NotificarInputDTO
from notificaciones.application.shared.dtos.notificacion_output_dto import NotificacionOutputDTO


class INotificarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: NotificarInputDTO) -> list[NotificacionOutputDTO]: ...
