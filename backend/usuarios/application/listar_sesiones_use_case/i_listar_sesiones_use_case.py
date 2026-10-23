# usuarios/application/listar_sesiones_use_case/i_listar_sesiones_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.listar_sesiones_use_case.dtos.listar_sesiones_input_dto import ListarSesionesInputDTO
from usuarios.application.listar_sesiones_use_case.dtos.sesion_activa_output_dto import SesionActivaOutputDTO


class IListarSesionesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarSesionesInputDTO) -> list[SesionActivaOutputDTO]: ...
