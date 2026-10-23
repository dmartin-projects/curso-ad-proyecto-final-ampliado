# usuarios/application/completar_segundo_factor_use_case/i_completar_segundo_factor_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.completar_segundo_factor_use_case.dtos.completar_segundo_factor_input_dto import (
    CompletarSegundoFactorInputDTO,
)
from usuarios.application.shared.dtos.login_pendiente_output_dto import LoginPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO


class ICompletarSegundoFactorUseCase(ABC):
    @abstractmethod
    def ejecutar(
        self, entrada: CompletarSegundoFactorInputDTO
    ) -> tuple[SesionAbiertaOutputDTO, LoginPendienteOutputDTO]: ...
