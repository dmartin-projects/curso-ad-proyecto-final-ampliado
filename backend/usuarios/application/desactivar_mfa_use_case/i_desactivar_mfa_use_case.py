# usuarios/application/desactivar_mfa_use_case/i_desactivar_mfa_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.desactivar_mfa_use_case.dtos.desactivar_mfa_input_dto import DesactivarMfaInputDTO


class IDesactivarMfaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: DesactivarMfaInputDTO) -> None: ...
