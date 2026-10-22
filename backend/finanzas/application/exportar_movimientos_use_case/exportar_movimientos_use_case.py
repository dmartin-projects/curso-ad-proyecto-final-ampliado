# finanzas/application/exportar_movimientos_use_case/exportar_movimientos_use_case.py (módulo 87)
from collections.abc import Iterator

from core.domain.enums.rol import Rol
from finanzas.application.exportar_movimientos_use_case.dtos.exportar_movimientos_input_dto import (
    ExportarMovimientosInputDTO,
)
from finanzas.application.exportar_movimientos_use_case.dtos.movimiento_exportado_output_dto import (
    MovimientoExportadoOutputDTO,
)
from finanzas.application.exportar_movimientos_use_case.i_exportar_movimientos_use_case import (
    IExportarMovimientosUseCase,
)
from finanzas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService
from finanzas.domain.repositories.queries.movimientos_query import MovimientosQuery


class ExportarMovimientosUseCase(IExportarMovimientosUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, movimientos: IMovimientoQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ExportarMovimientosInputDTO) -> Iterator[MovimientoExportadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        query = MovimientosQuery(entrada.hogar_id, entrada.filtros, entrada.orden)
        # un generador: las filas se leen y se traducen a medida que se escriben (el CSV va en streaming)
        return (MovimientoExportadoOutputDTO.desde_read_model(f) for f in self.movimientos.exportar(query))
