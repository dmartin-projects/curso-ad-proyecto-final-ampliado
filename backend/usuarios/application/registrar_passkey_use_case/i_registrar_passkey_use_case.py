# usuarios/application/registrar_passkey_use_case/i_registrar_passkey_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.registrar_passkey_use_case.dtos.registrar_passkey_input_dto import RegistrarPasskeyInputDTO


class IRegistrarPasskeyUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RegistrarPasskeyInputDTO) -> int: ...
