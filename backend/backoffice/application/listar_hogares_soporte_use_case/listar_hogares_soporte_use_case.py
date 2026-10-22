# backoffice/application/listar_hogares_soporte_use_case/listar_hogares_soporte_use_case.py (módulo 88)
from backoffice.application.listar_hogares_soporte_use_case.dtos.listar_hogares_soporte_input_dto import (
    ListarHogaresSoporteInputDTO,
)
from backoffice.application.listar_hogares_soporte_use_case.i_listar_hogares_soporte_use_case import (
    IListarHogaresSoporteUseCase,
)
from backoffice.application.shared.dtos.hogar_soporte_output_dto import HogarSoporteOutputDTO
from backoffice.domain.repositories.i_hogar_soporte_query_service import IHogarSoporteQueryService
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class ListarHogaresSoporteUseCase(IListarHogaresSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, hogares: IHogarSoporteQueryService):
        self.hogares = hogares

    def ejecutar(self, entrada: ListarHogaresSoporteInputDTO) -> PaginaOutputDTO[HogarSoporteOutputDTO]:
        return PaginaOutputDTO.desde_pagina(self.hogares.listar(entrada.query), HogarSoporteOutputDTO.desde_read_model)
