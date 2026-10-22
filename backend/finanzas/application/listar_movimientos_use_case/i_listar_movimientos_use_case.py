# finanzas/application/listar_movimientos_use_case/i_listar_movimientos_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from finanzas.application.listar_movimientos_use_case.dtos.listar_movimientos_input_dto import ListarMovimientosInputDTO
from finanzas.application.shared.dtos.movimiento_listado_output_dto import MovimientoListadoOutputDTO


class IListarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarMovimientosInputDTO) -> PaginaOutputDTO[MovimientoListadoOutputDTO]: ...
