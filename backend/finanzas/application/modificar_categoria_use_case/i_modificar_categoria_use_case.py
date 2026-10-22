# finanzas/application/modificar_categoria_use_case/i_modificar_categoria_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.modificar_categoria_use_case.dtos.modificar_categoria_input_dto import (
    ModificarCategoriaInputDTO,
)
from finanzas.application.shared.dtos.categoria_output_dto import CategoriaOutputDTO


class IModificarCategoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ModificarCategoriaInputDTO) -> CategoriaOutputDTO: ...
