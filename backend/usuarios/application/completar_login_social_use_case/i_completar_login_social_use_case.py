# usuarios/application/completar_login_social_use_case/i_completar_login_social_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.completar_login_social_use_case.dtos.completar_login_social_input_dto import (
    CompletarLoginSocialInputDTO,
)
from usuarios.application.completar_login_social_use_case.dtos.login_social_completado_output_dto import (
    LoginSocialCompletadoOutputDTO,
)


class ICompletarLoginSocialUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CompletarLoginSocialInputDTO) -> LoginSocialCompletadoOutputDTO: ...
