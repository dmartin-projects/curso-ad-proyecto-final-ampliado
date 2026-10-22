# finanzas/application/exportar_movimientos_use_case/i_exportar_movimientos_use_case.py (módulo 87)
from abc import ABC, abstractmethod
from collections.abc import Iterator

from finanzas.application.exportar_movimientos_use_case.dtos.exportar_movimientos_input_dto import (
    ExportarMovimientosInputDTO,
)
from finanzas.application.exportar_movimientos_use_case.dtos.movimiento_exportado_output_dto import (
    MovimientoExportadoOutputDTO,
)


class IExportarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ExportarMovimientosInputDTO) -> Iterator[MovimientoExportadoOutputDTO]: ...
