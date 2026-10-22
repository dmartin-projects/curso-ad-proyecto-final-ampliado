# usuarios/application/solicitar_registro_use_case/i_solicitar_registro_use_case.py (módulos 35 y 88)
from abc import ABC, abstractmethod

from usuarios.application.solicitar_registro_use_case.dtos.solicitar_registro_input_dto import SolicitarRegistroInputDTO


class ISolicitarRegistroUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: SolicitarRegistroInputDTO) -> None: ...
