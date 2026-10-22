# finanzas/application/modificar_presupuesto_use_case/i_modificar_presupuesto_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.modificar_presupuesto_use_case.dtos.modificar_presupuesto_input_dto import (
    ModificarPresupuestoInputDTO,
)
from finanzas.application.shared.dtos.presupuesto_output_dto import PresupuestoOutputDTO


class IModificarPresupuestoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ModificarPresupuestoInputDTO) -> PresupuestoOutputDTO: ...
