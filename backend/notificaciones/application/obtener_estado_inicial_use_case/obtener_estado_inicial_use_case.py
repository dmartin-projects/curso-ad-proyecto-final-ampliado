# notificaciones/application/obtener_estado_inicial_use_case/obtener_estado_inicial_use_case.py (módulo 88)
from notificaciones.application.obtener_estado_inicial_use_case.dtos.estado_inicial_output_dto import (
    EstadoInicialOutputDTO,
)
from notificaciones.application.obtener_estado_inicial_use_case.dtos.obtener_estado_inicial_input_dto import (
    ObtenerEstadoInicialInputDTO,
)
from notificaciones.application.obtener_estado_inicial_use_case.i_obtener_estado_inicial_use_case import (
    IObtenerEstadoInicialUseCase,
)
from notificaciones.application.ports.i_destinatarios import IDestinatarios
from notificaciones.domain.repositories.i_notificacion_query_service import INotificacionQueryService


class ObtenerEstadoInicialUseCase(IObtenerEstadoInicialUseCase):
    """Lo que necesita un WebSocket al conectarse: a qué hogares escuchar y cuántas notificaciones hay sin leer."""

    def __init__(self, *, destinatarios: IDestinatarios, notificaciones: INotificacionQueryService):
        self.destinatarios, self.notificaciones = destinatarios, notificaciones

    def ejecutar(self, entrada: ObtenerEstadoInicialInputDTO) -> EstadoInicialOutputDTO:
        return EstadoInicialOutputDTO(
            hogares=tuple(self.destinatarios.hogares(entrada.usuario_id)),
            no_leidas=self.notificaciones.contar_no_leidas(entrada.usuario_id),
        )
