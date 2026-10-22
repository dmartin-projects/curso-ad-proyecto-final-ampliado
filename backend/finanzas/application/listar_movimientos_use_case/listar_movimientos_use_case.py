# finanzas/application/listar_movimientos_use_case/listar_movimientos_use_case.py (módulo 87)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from core.domain.enums.rol import Rol
from finanzas.application.listar_movimientos_use_case.dtos.listar_movimientos_input_dto import ListarMovimientosInputDTO
from finanzas.application.listar_movimientos_use_case.i_listar_movimientos_use_case import IListarMovimientosUseCase
from finanzas.application.shared.dtos.movimiento_listado_output_dto import MovimientoListadoOutputDTO
from finanzas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from finanzas.domain.repositories.queries.movimientos_query import MovimientosQuery


class ListarMovimientosUseCase(IListarMovimientosUseCase):
    """Un use case de CONSULTA: sin transacción ni eventos; pide al query service y traduce a OutputDTOs."""

    rol_minimo = Rol.LECTOR

    def __init__(self, *, movimientos: IMovimientoQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ListarMovimientosInputDTO) -> PaginaOutputDTO[MovimientoListadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        query = MovimientosQuery(entrada.hogar_id, entrada.filtros, entrada.orden, entrada.paginacion)
        return PaginaOutputDTO.desde_pagina(self.movimientos.listar(query), MovimientoListadoOutputDTO.desde_read_model)
