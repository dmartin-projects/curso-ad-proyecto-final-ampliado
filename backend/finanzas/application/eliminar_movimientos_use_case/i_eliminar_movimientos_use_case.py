# finanzas/application/eliminar_movimientos_use_case/i_eliminar_movimientos_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from finanzas.application.eliminar_movimientos_use_case.dtos.eliminar_movimientos_input_dto import (
    EliminarMovimientosInputDTO,
)


class IEliminarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarMovimientosInputDTO) -> list[int]: ...
