# asistente/application/asignar_plan_use_case/i_asignar_plan_use_case.py (módulo 98)
from abc import ABC, abstractmethod

from asistente.application.asignar_plan_use_case.dtos.asignar_plan_input_dto import AsignarPlanInputDTO


class IAsignarPlanUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: AsignarPlanInputDTO) -> None:
        """Lo hace el personal (manage.py plan_asistente); con pagos, lo haría el webhook del proveedor de pagos."""
