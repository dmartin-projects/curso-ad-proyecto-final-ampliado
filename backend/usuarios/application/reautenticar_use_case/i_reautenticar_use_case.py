# usuarios/application/reautenticar_use_case/i_reautenticar_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.reautenticar_use_case.dtos.reautenticar_input_dto import ReautenticarInputDTO
from usuarios.application.shared.dtos.autenticacion_output_dto import AutenticacionOutputDTO


class IReautenticarUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ReautenticarInputDTO) -> AutenticacionOutputDTO: ...
