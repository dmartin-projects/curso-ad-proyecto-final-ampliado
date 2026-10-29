# finanzas/application/obtener_totales_movimientos_use_case/obtener_totales_movimientos_use_case.py — un use case de
# CONSULTA: cuántos movimientos cumplen unos filtros y cuánto suman (módulo 95)
from core.domain.enums.rol import Rol
from finanzas.application.obtener_totales_movimientos_use_case.dtos.obtener_totales_movimientos_input_dto import (
    ObtenerTotalesMovimientosInputDTO,
)
from finanzas.application.obtener_totales_movimientos_use_case.dtos.totales_de_movimientos_output_dto import (
    TotalesDeMovimientosOutputDTO,
)
from finanzas.application.obtener_totales_movimientos_use_case.i_obtener_totales_movimientos_use_case import (
    IObtenerTotalesMovimientosUseCase,
)
from finanzas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from finanzas.domain.repositories.queries.movimientos_query import MovimientosQuery


class ObtenerTotalesMovimientosUseCase(IObtenerTotalesMovimientosUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, movimientos: IMovimientoQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ObtenerTotalesMovimientosInputDTO) -> TotalesDeMovimientosOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        totales = self.movimientos.totales(MovimientosQuery(entrada.hogar_id, entrada.filtros))
        return TotalesDeMovimientosOutputDTO.desde_read_model(totales)
