# hogares/application/salir_del_hogar_use_case/i_salir_del_hogar_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.salir_del_hogar_use_case.dtos.salir_del_hogar_input_dto import SalirDelHogarInputDTO


class ISalirDelHogarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: SalirDelHogarInputDTO) -> None: ...
