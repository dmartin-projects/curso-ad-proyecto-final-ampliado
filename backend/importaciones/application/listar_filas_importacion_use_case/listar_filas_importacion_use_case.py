# importaciones/application/listar_filas_importacion_use_case/listar_filas_importacion_use_case.py (módulo 88)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from core.domain.enums.rol import Rol
from importaciones.application.listar_filas_importacion_use_case.dtos.listar_filas_importacion_input_dto import (
    ListarFilasImportacionInputDTO,
)
from importaciones.application.listar_filas_importacion_use_case.i_listar_filas_importacion_use_case import (
    IListarFilasImportacionUseCase,
)
from importaciones.application.shared.dtos.fila_listada_output_dto import FilaListadaOutputDTO
from importaciones.domain.repositories.i_importacion_query_service import IImportacionQueryService
from importaciones.domain.repositories.queries.filas_query import FilasQuery


class ListarFilasImportacionUseCase(IListarFilasImportacionUseCase):
    """La vista previa. None si la importación no es de ese hogar."""

    rol_minimo = Rol.LECTOR

    def __init__(self, *, importaciones: IImportacionQueryService):
        self.importaciones = importaciones

    def ejecutar(self, entrada: ListarFilasImportacionInputDTO) -> PaginaOutputDTO[FilaListadaOutputDTO] | None:
        entrada.actor.exigir(self.rol_minimo)
        if self.importaciones.detalle(entrada.hogar_id, entrada.importacion_id) is None:
            return None
        pagina = self.importaciones.filas(FilasQuery(entrada.importacion_id, entrada.accion, entrada.paginacion))
        return PaginaOutputDTO.desde_pagina(pagina, FilaListadaOutputDTO.desde_read_model)
