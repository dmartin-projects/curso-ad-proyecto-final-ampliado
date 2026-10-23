# usuarios/application/borrar_passkey_use_case/i_borrar_passkey_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.borrar_passkey_use_case.dtos.borrar_passkey_input_dto import BorrarPasskeyInputDTO


class IBorrarPasskeyUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: BorrarPasskeyInputDTO) -> None: ...
