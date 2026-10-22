# finanzas/application/recategorizar_movimientos_use_case/i_recategorizar_movimientos_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.recategorizar_movimientos_use_case.dtos.recategorizar_movimientos_input_dto import (
    RecategorizarMovimientosInputDTO,
)


class IRecategorizarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RecategorizarMovimientosInputDTO) -> int: ...
