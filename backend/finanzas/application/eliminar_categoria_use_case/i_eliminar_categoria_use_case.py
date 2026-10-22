# finanzas/application/eliminar_categoria_use_case/i_eliminar_categoria_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.eliminar_categoria_use_case.dtos.eliminar_categoria_input_dto import EliminarCategoriaInputDTO


class IEliminarCategoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: EliminarCategoriaInputDTO) -> None: ...
