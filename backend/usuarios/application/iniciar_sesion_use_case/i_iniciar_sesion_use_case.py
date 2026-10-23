# usuarios/application/iniciar_sesion_use_case/i_iniciar_sesion_use_case.py (módulos 35, 91 y 92)
from abc import ABC, abstractmethod

from usuarios.application.iniciar_sesion_use_case.dtos.iniciar_sesion_input_dto import IniciarSesionInputDTO
from usuarios.application.shared.dtos.segundo_factor_pendiente_output_dto import SegundoFactorPendienteOutputDTO
from usuarios.application.shared.dtos.sesion_abierta_output_dto import SesionAbiertaOutputDTO


class IIniciarSesionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: IniciarSesionInputDTO) -> SesionAbiertaOutputDTO | SegundoFactorPendienteOutputDTO: ...
