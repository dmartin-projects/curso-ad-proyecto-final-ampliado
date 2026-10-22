# finanzas/application/desconciliar_movimientos_use_case/i_desconciliar_movimientos_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from finanzas.application.desconciliar_movimientos_use_case.dtos.desconciliar_movimientos_input_dto import (
    DesconciliarMovimientosInputDTO,
)


class IDesconciliarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: DesconciliarMovimientosInputDTO) -> int: ...
