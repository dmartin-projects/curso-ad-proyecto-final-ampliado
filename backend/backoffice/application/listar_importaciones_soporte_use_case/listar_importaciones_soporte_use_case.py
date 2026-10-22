# backoffice/application/listar_importaciones_soporte_use_case/listar_importaciones_soporte_use_case.py (módulo 88)
from backoffice.application.listar_importaciones_soporte_use_case.dtos.listar_importaciones_soporte_input_dto import (
    ListarImportacionesSoporteInputDTO,
)
from backoffice.application.listar_importaciones_soporte_use_case.i_listar_importaciones_soporte_use_case import (
    IListarImportacionesSoporteUseCase,
)
from backoffice.application.shared.dtos.importacion_soporte_output_dto import ImportacionSoporteOutputDTO
from backoffice.domain.repositories.i_importacion_soporte_query_service import IImportacionSoporteQueryService
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class ListarImportacionesSoporteUseCase(IListarImportacionesSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, importaciones: IImportacionSoporteQueryService):
        self.importaciones = importaciones

    def ejecutar(self, entrada: ListarImportacionesSoporteInputDTO) -> PaginaOutputDTO[ImportacionSoporteOutputDTO]:
        return PaginaOutputDTO.desde_pagina(
            self.importaciones.listar(entrada.query), ImportacionSoporteOutputDTO.desde_read_model
        )
