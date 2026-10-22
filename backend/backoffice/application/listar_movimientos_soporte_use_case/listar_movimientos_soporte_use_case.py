# backoffice/application/listar_movimientos_soporte_use_case/listar_movimientos_soporte_use_case.py (módulo 88)
from backoffice.application.listar_movimientos_soporte_use_case.dtos.listar_movimientos_soporte_input_dto import (
    ListarMovimientosSoporteInputDTO,
)
from backoffice.application.listar_movimientos_soporte_use_case.i_listar_movimientos_soporte_use_case import (
    IListarMovimientosSoporteUseCase,
)
from backoffice.application.shared.dtos.movimiento_soporte_output_dto import MovimientoSoporteOutputDTO
from backoffice.domain.repositories.i_movimiento_soporte_query_service import IMovimientoSoporteQueryService
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class ListarMovimientosSoporteUseCase(IListarMovimientosSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, movimientos: IMovimientoSoporteQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ListarMovimientosSoporteInputDTO) -> PaginaOutputDTO[MovimientoSoporteOutputDTO]:
        return PaginaOutputDTO.desde_pagina(
            self.movimientos.listar(entrada.query), MovimientoSoporteOutputDTO.desde_read_model
        )
