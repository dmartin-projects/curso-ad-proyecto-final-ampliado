# finanzas/application/conciliar_movimientos_use_case/i_conciliar_movimientos_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from finanzas.application.conciliar_movimientos_use_case.dtos.conciliar_movimientos_input_dto import (
    ConciliarMovimientosInputDTO,
)


class IConciliarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConciliarMovimientosInputDTO) -> list[int]: ...
