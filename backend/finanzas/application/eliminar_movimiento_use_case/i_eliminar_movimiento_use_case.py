# finanzas/application/eliminar_movimiento_use_case/i_eliminar_movimiento_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.eliminar_movimiento_use_case.dtos.eliminar_movimiento_input_dto import (
    EliminarMovimientoInputDTO,
)


class IEliminarMovimientoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarMovimientoInputDTO) -> None: ...
