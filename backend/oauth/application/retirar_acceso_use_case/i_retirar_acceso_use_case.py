# oauth/application/retirar_acceso_use_case/i_retirar_acceso_use_case.py (ejercicio 1 del módulo 90)
from abc import ABC, abstractmethod

from oauth.application.retirar_acceso_use_case.dtos.retirar_acceso_input_dto import RetirarAccesoInputDTO


class IRetirarAccesoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: RetirarAccesoInputDTO) -> int: ...
