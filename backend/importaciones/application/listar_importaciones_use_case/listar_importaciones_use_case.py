# importaciones/application/listar_importaciones_use_case/listar_importaciones_use_case.py (módulo 88)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from core.domain.enums.rol import Rol
from importaciones.application.listar_importaciones_use_case.dtos.listar_importaciones_input_dto import (
    ListarImportacionesInputDTO,
)
from importaciones.application.listar_importaciones_use_case.i_listar_importaciones_use_case import (
    IListarImportacionesUseCase,
)
from importaciones.application.shared.dtos.importacion_listada_output_dto import ImportacionListadaOutputDTO
from importaciones.domain.repositories.i_importacion_query_service import IImportacionQueryService
from importaciones.domain.repositories.queries.importaciones_query import ImportacionesQuery


class ListarImportacionesUseCase(IListarImportacionesUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, importaciones: IImportacionQueryService):
        self.importaciones = importaciones

    def ejecutar(self, entrada: ListarImportacionesInputDTO) -> PaginaOutputDTO[ImportacionListadaOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        query = ImportacionesQuery(
            entrada.hogar_id, entrada.estado, entrada.cuenta_id, entrada.orden, entrada.paginacion
        )
        pagina = self.importaciones.listar(query)
        return PaginaOutputDTO.desde_pagina(pagina, ImportacionListadaOutputDTO.desde_read_model)
