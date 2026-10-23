# usuarios/application/empezar_totp_use_case/i_empezar_totp_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.empezar_totp_use_case.dtos.alta_totp_output_dto import AltaTotpOutputDTO
from usuarios.application.empezar_totp_use_case.dtos.empezar_totp_input_dto import EmpezarTotpInputDTO


class IEmpezarTotpUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EmpezarTotpInputDTO) -> AltaTotpOutputDTO: ...
