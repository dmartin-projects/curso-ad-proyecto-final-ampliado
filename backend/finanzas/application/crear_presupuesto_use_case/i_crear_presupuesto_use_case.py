# finanzas/application/crear_presupuesto_use_case/i_crear_presupuesto_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.crear_presupuesto_use_case.dtos.crear_presupuesto_input_dto import CrearPresupuestoInputDTO
from finanzas.application.shared.dtos.presupuesto_output_dto import PresupuestoOutputDTO


class ICrearPresupuestoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CrearPresupuestoInputDTO) -> PresupuestoOutputDTO: ...
