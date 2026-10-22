# finanzas/application/apuntar_movimientos_use_case/i_apuntar_movimientos_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from finanzas.application.apuntar_movimientos_use_case.dtos.apuntar_movimientos_input_dto import (
    ApuntarMovimientosInputDTO,
)


class IApuntarMovimientosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ApuntarMovimientosInputDTO) -> list[int]: ...
