# notificaciones/application/listar_notificaciones_use_case/listar_notificaciones_use_case.py (módulo 88)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from notificaciones.application.listar_notificaciones_use_case.dtos.listar_notificaciones_input_dto import (
    ListarNotificacionesInputDTO,
)
from notificaciones.application.listar_notificaciones_use_case.i_listar_notificaciones_use_case import (
    IListarNotificacionesUseCase,
)
from notificaciones.application.shared.dtos.notificacion_listada_output_dto import NotificacionListadaOutputDTO
from notificaciones.domain.repositories.i_notificacion_query_service import INotificacionQueryService
from notificaciones.domain.repositories.queries.notificaciones_query import NotificacionesQuery


class ListarNotificacionesUseCase(IListarNotificacionesUseCase):
    """Las de quien pregunta: no hay hogar ni rol que comprobar (el usuario_id es el de la sesión)."""

    def __init__(self, *, notificaciones: INotificacionQueryService):
        self.notificaciones = notificaciones

    def ejecutar(self, entrada: ListarNotificacionesInputDTO) -> PaginaOutputDTO[NotificacionListadaOutputDTO]:
        query = NotificacionesQuery(
            entrada.usuario_id, entrada.leida, entrada.tipo, entrada.hogar_id, entrada.paginacion
        )
        pagina = self.notificaciones.listar(query)
        return PaginaOutputDTO.desde_pagina(pagina, NotificacionListadaOutputDTO.desde_read_model)
