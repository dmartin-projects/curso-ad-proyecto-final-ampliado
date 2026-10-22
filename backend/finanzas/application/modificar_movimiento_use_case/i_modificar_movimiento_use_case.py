# finanzas/application/modificar_movimiento_use_case/i_modificar_movimiento_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.modificar_movimiento_use_case.dtos.modificar_movimiento_input_dto import (
    ModificarMovimientoInputDTO,
)
from finanzas.application.shared.dtos.movimiento_output_dto import MovimientoOutputDTO


class IModificarMovimientoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ModificarMovimientoInputDTO) -> MovimientoOutputDTO: ...
