# backoffice/application/obtener_hogar_soporte_use_case/i_obtener_hogar_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_hogar_soporte_use_case.dtos.obtener_hogar_soporte_input_dto import (
    ObtenerHogarSoporteInputDTO,
)
from backoffice.application.shared.dtos.hogar_soporte_output_dto import HogarSoporteOutputDTO


class IObtenerHogarSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerHogarSoporteInputDTO) -> HogarSoporteOutputDTO | None: ...
