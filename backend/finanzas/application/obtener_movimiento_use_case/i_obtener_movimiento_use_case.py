# finanzas/application/obtener_movimiento_use_case/i_obtener_movimiento_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.obtener_movimiento_use_case.dtos.obtener_movimiento_input_dto import ObtenerMovimientoInputDTO
from finanzas.application.shared.dtos.movimiento_listado_output_dto import MovimientoListadoOutputDTO


class IObtenerMovimientoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerMovimientoInputDTO) -> MovimientoListadoOutputDTO | None: ...
