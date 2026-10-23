# usuarios/application/empezar_registro_passkey_use_case/i_empezar_registro_passkey_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.empezar_registro_passkey_use_case.dtos.empezar_registro_passkey_input_dto import (
    EmpezarRegistroPasskeyInputDTO,
)


class IEmpezarRegistroPasskeyUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EmpezarRegistroPasskeyInputDTO) -> dict: ...
