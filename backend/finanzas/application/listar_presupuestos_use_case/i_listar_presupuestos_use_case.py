# finanzas/application/listar_presupuestos_use_case/i_listar_presupuestos_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.listar_presupuestos_use_case.dtos.listar_presupuestos_input_dto import (
    ListarPresupuestosInputDTO,
)
from finanzas.application.shared.dtos.presupuesto_con_gastado_output_dto import PresupuestoConGastadoOutputDTO


class IListarPresupuestosUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarPresupuestosInputDTO) -> list[PresupuestoConGastadoOutputDTO]: ...
