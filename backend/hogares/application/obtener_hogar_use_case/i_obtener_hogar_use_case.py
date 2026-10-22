# hogares/application/obtener_hogar_use_case/i_obtener_hogar_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.obtener_hogar_use_case.dtos.obtener_hogar_input_dto import ObtenerHogarInputDTO
from hogares.application.shared.dtos.hogar_listado_output_dto import HogarListadoOutputDTO


class IObtenerHogarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerHogarInputDTO) -> HogarListadoOutputDTO | None: ...
