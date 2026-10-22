# finanzas/application/obtener_dashboard_use_case/i_obtener_dashboard_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.obtener_dashboard_use_case.dtos.dashboard_output_dto import DashboardOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.obtener_dashboard_input_dto import ObtenerDashboardInputDTO


class IObtenerDashboardUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerDashboardInputDTO) -> DashboardOutputDTO: ...
