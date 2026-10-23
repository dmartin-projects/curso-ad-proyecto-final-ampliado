# usuarios/application/comprobar_autenticacion_reciente_use_case/i_comprobar_autenticacion_reciente_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.comprobar_autenticacion_reciente_use_case.dtos.comprobar_autenticacion_reciente_input_dto import (
    ComprobarAutenticacionRecienteInputDTO,
)


class IComprobarAutenticacionRecienteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ComprobarAutenticacionRecienteInputDTO) -> bool: ...
