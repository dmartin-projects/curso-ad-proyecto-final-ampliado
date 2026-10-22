# finanzas/application/eliminar_presupuesto_use_case/i_eliminar_presupuesto_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.eliminar_presupuesto_use_case.dtos.eliminar_presupuesto_input_dto import (
    EliminarPresupuestoInputDTO,
)


class IEliminarPresupuestoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarPresupuestoInputDTO) -> None: ...
