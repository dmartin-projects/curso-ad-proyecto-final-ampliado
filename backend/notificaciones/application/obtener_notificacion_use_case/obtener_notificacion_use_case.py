# notificaciones/application/obtener_notificacion_use_case/obtener_notificacion_use_case.py (módulo 88)
from notificaciones.application.obtener_notificacion_use_case.dtos.obtener_notificacion_input_dto import (
    ObtenerNotificacionInputDTO,
)
from notificaciones.application.obtener_notificacion_use_case.i_obtener_notificacion_use_case import (
    IObtenerNotificacionUseCase,
)
from notificaciones.application.shared.dtos.notificacion_listada_output_dto import NotificacionListadaOutputDTO
from notificaciones.domain.repositories.i_notificacion_query_service import INotificacionQueryService


class ObtenerNotificacionUseCase(IObtenerNotificacionUseCase):
    def __init__(self, *, notificaciones: INotificacionQueryService):
        self.notificaciones = notificaciones

    def ejecutar(self, entrada: ObtenerNotificacionInputDTO) -> NotificacionListadaOutputDTO | None:
        leida = self.notificaciones.detalle(entrada.usuario_id, entrada.notificacion_id)
        return None if leida is None else NotificacionListadaOutputDTO.desde_read_model(leida)
