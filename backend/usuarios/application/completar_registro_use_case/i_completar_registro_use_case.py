# usuarios/application/completar_registro_use_case/i_completar_registro_use_case.py (módulos 35 y 88)
from abc import ABC, abstractmethod

from usuarios.application.completar_registro_use_case.dtos.completar_registro_input_dto import CompletarRegistroInputDTO


class ICompletarRegistroUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CompletarRegistroInputDTO) -> None: ...
