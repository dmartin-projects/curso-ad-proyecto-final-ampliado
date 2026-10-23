# usuarios/application/iniciar_sesion_use_case/i_iniciar_sesion_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.iniciar_sesion_use_case.dtos.par_de_tokens_output_dto import ParDeTokensOutputDTO


class IIniciarSesionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: IniciarSesionInputDTO) -> ParDeTokensOutputDTO | None: ...
