# notificaciones/application/listar_notificaciones_use_case/i_listar_notificaciones_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from notificaciones.application.listar_notificaciones_use_case.dtos.listar_notificaciones_input_dto import (
    ListarNotificacionesInputDTO,
)
from notificaciones.application.shared.dtos.notificacion_listada_output_dto import NotificacionListadaOutputDTO


class IListarNotificacionesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarNotificacionesInputDTO) -> PaginaOutputDTO[NotificacionListadaOutputDTO]: ...
