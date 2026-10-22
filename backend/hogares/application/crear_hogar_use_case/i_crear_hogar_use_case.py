# hogares/application/crear_hogar_use_case/i_crear_hogar_use_case.py (módulos 71 y 88)
from abc import ABC, abstractmethod

from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.shared.dtos.hogar_output_dto import HogarOutputDTO


class ICrearHogarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CrearHogarInputDTO) -> HogarOutputDTO: ...
