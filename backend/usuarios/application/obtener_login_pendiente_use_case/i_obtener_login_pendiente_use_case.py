# usuarios/application/obtener_login_pendiente_use_case/i_obtener_login_pendiente_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.obtener_login_pendiente_use_case.dtos.obtener_login_pendiente_input_dto import (
    ObtenerLoginPendienteInputDTO,
)
from usuarios.application.shared.dtos.login_pendiente_output_dto import LoginPendienteOutputDTO


class IObtenerLoginPendienteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerLoginPendienteInputDTO) -> LoginPendienteOutputDTO: ...
