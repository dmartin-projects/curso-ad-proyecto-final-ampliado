# usuarios/application/empezar_login_social_use_case/i_empezar_login_social_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.empezar_login_social_use_case.dtos.empezar_login_social_input_dto import (
    EmpezarLoginSocialInputDTO,
)
from usuarios.application.empezar_login_social_use_case.dtos.ida_al_proveedor_output_dto import (
    IdaAlProveedorOutputDTO,
)


class IEmpezarLoginSocialUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EmpezarLoginSocialInputDTO) -> IdaAlProveedorOutputDTO: ...
