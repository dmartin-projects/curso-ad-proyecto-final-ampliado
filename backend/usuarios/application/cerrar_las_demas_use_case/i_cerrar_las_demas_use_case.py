# usuarios/application/cerrar_las_demas_use_case/i_cerrar_las_demas_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.cerrar_las_demas_use_case.dtos.cerrar_las_demas_input_dto import CerrarLasDemasInputDTO


class ICerrarLasDemasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CerrarLasDemasInputDTO) -> int: ...
