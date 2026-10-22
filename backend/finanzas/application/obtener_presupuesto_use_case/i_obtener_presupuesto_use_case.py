# finanzas/application/obtener_presupuesto_use_case/i_obtener_presupuesto_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.obtener_presupuesto_use_case.dtos.obtener_presupuesto_input_dto import (
    ObtenerPresupuestoInputDTO,
)
from finanzas.application.shared.dtos.presupuesto_con_gastado_output_dto import PresupuestoConGastadoOutputDTO


class IObtenerPresupuestoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerPresupuestoInputDTO) -> PresupuestoConGastadoOutputDTO | None: ...
