# finanzas/application/eliminar_cuenta_use_case/i_eliminar_cuenta_use_case.py (ejercicio 1 del módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.eliminar_cuenta_use_case.dtos.eliminar_cuenta_input_dto import EliminarCuentaInputDTO


class IEliminarCuentaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarCuentaInputDTO) -> None: ...
