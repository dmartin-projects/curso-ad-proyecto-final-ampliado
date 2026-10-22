# finanzas/application/crear_categorias_por_defecto_use_case/i_crear_categorias_por_defecto_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.crear_categorias_por_defecto_use_case.dtos.crear_categorias_por_defecto_input_dto import (
    CrearCategoriasPorDefectoInputDTO,
)


class ICrearCategoriasPorDefectoUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: CrearCategoriasPorDefectoInputDTO) -> int: ...
