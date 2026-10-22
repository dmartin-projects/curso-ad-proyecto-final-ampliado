# backoffice/application/obtener_usuario_soporte_use_case/i_obtener_usuario_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_usuario_soporte_use_case.dtos.obtener_usuario_soporte_input_dto import (
    ObtenerUsuarioSoporteInputDTO,
)
from backoffice.application.shared.dtos.usuario_soporte_output_dto import UsuarioSoporteOutputDTO


class IObtenerUsuarioSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerUsuarioSoporteInputDTO) -> UsuarioSoporteOutputDTO | None: ...
