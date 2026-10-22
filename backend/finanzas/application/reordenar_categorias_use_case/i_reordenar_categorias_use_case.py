# finanzas/application/reordenar_categorias_use_case/i_reordenar_categorias_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.reordenar_categorias_use_case.dtos.reordenar_categorias_input_dto import (
    ReordenarCategoriasInputDTO,
)


class IReordenarCategoriasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ReordenarCategoriasInputDTO) -> None: ...
