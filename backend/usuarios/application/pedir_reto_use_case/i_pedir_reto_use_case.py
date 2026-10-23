# usuarios/application/pedir_reto_use_case/i_pedir_reto_use_case.py (módulo 92)
from abc import ABC, abstractmethod

from usuarios.application.pedir_reto_use_case.dtos.pedir_reto_input_dto import PedirRetoInputDTO


class IPedirRetoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: PedirRetoInputDTO) -> dict: ...
