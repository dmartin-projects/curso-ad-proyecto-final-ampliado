# backoffice/application/listar_usuarios_soporte_use_case/i_listar_usuarios_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_usuarios_soporte_use_case.dtos.listar_usuarios_soporte_input_dto import (
    ListarUsuariosSoporteInputDTO,
)
from backoffice.application.shared.dtos.usuario_soporte_output_dto import UsuarioSoporteOutputDTO
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class IListarUsuariosSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarUsuariosSoporteInputDTO) -> PaginaOutputDTO[UsuarioSoporteOutputDTO]: ...
