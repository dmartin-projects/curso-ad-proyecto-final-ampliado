# finanzas/application/crear_categoria_use_case/i_crear_categoria_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.crear_categoria_use_case.dtos.crear_categoria_input_dto import CrearCategoriaInputDTO
from finanzas.application.shared.dtos.categoria_output_dto import CategoriaOutputDTO


class ICrearCategoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CrearCategoriaInputDTO) -> CategoriaOutputDTO: ...
