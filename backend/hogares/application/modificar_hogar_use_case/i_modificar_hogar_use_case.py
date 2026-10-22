# hogares/application/modificar_hogar_use_case/i_modificar_hogar_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.modificar_hogar_use_case.dtos.modificar_hogar_input_dto import ModificarHogarInputDTO
from hogares.application.shared.dtos.hogar_output_dto import HogarOutputDTO


class IModificarHogarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ModificarHogarInputDTO) -> HogarOutputDTO: ...
