# usuarios/application/obtener_autenticacion_use_case/i_obtener_autenticacion_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.obtener_autenticacion_use_case.dtos.obtener_autenticacion_input_dto import (
    ObtenerAutenticacionInputDTO,
)
from usuarios.application.shared.dtos.autenticacion_output_dto import AutenticacionOutputDTO


class IObtenerAutenticacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerAutenticacionInputDTO) -> AutenticacionOutputDTO | None: ...
