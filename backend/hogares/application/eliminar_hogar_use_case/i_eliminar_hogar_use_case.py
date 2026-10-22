# hogares/application/eliminar_hogar_use_case/i_eliminar_hogar_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.application.eliminar_hogar_use_case.dtos.eliminar_hogar_input_dto import EliminarHogarInputDTO


class IEliminarHogarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarHogarInputDTO) -> None: ...
