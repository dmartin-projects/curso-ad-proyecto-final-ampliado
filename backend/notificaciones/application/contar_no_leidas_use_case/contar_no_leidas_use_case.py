# notificaciones/application/contar_no_leidas_use_case/contar_no_leidas_use_case.py (módulo 88)
from notificaciones.application.contar_no_leidas_use_case.dtos.contar_no_leidas_input_dto import ContarNoLeidasInputDTO
from notificaciones.application.contar_no_leidas_use_case.i_contar_no_leidas_use_case import IContarNoLeidasUseCase
from notificaciones.domain.repositories.i_notificacion_query_service import INotificacionQueryService


class ContarNoLeidasUseCase(IContarNoLeidasUseCase):
    def __init__(self, *, notificaciones: INotificacionQueryService):
        self.notificaciones = notificaciones

    def ejecutar(self, entrada: ContarNoLeidasInputDTO) -> int:
        return self.notificaciones.contar_no_leidas(entrada.usuario_id)
