# asistente/application/contar_hogares_sin_cuota_use_case/i_contar_hogares_sin_cuota_use_case.py (98, ejercicio 2)
from abc import ABC, abstractmethod

from asistente.application.contar_hogares_sin_cuota_use_case.dtos.contar_hogares_sin_cuota_input_dto import (
    ContarHogaresSinCuotaInputDTO,
)


class IContarHogaresSinCuotaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ContarHogaresSinCuotaInputDTO) -> int:
        """Cuántos hogares han gastado ya la cuota del mes de su plan."""
