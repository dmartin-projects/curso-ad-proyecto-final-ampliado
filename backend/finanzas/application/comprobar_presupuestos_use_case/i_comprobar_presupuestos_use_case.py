# finanzas/application/comprobar_presupuestos_use_case/i_comprobar_presupuestos_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.comprobar_presupuestos_use_case.dtos.comprobar_presupuestos_input_dto import (
    ComprobarPresupuestosInputDTO,
)
from finanzas.application.shared.dtos.presupuesto_output_dto import PresupuestoOutputDTO


class IComprobarPresupuestosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ComprobarPresupuestosInputDTO) -> list[PresupuestoOutputDTO]: ...
