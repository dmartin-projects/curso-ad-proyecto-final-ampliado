# asistente/application/consultar_cuota_use_case/i_consultar_cuota_use_case.py (módulo 98)
from abc import ABC, abstractmethod

from asistente.application.consultar_cuota_use_case.dtos.consultar_cuota_input_dto import ConsultarCuotaInputDTO
from asistente.application.shared.dtos.cuota_output_dto import CuotaOutputDTO


class IConsultarCuotaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConsultarCuotaInputDTO) -> CuotaOutputDTO:
        """Lo que lleva gastado quien pide (hoy) y su hogar (este mes), con los límites de su plan."""
