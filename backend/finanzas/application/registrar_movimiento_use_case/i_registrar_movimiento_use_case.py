# finanzas/application/registrar_movimiento_use_case/i_registrar_movimiento_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.registrar_movimiento_use_case.dtos.registrar_movimiento_input_dto import (
    RegistrarMovimientoInputDTO,
)
from finanzas.application.shared.dtos.movimiento_output_dto import MovimientoOutputDTO


class IRegistrarMovimientoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RegistrarMovimientoInputDTO) -> MovimientoOutputDTO: ...
