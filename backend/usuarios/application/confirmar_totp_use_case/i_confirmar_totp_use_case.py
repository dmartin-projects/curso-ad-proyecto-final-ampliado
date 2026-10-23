# usuarios/application/confirmar_totp_use_case/i_confirmar_totp_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.confirmar_totp_use_case.dtos.confirmar_totp_input_dto import ConfirmarTotpInputDTO


class IConfirmarTotpUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ConfirmarTotpInputDTO) -> list[str]: ...
