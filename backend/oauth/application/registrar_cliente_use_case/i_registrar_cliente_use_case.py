# oauth/application/registrar_cliente_use_case/i_registrar_cliente_use_case.py (módulo 90)
from abc import ABC, abstractmethod

from oauth.application.registrar_cliente_use_case.dtos.credenciales_output_dto import CredencialesOutputDTO
from oauth.application.registrar_cliente_use_case.dtos.registrar_cliente_input_dto import RegistrarClienteInputDTO


class IRegistrarClienteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RegistrarClienteInputDTO) -> CredencialesOutputDTO: ...
