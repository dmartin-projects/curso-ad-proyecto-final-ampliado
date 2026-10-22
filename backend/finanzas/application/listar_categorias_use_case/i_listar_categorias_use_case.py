# finanzas/application/listar_categorias_use_case/i_listar_categorias_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.listar_categorias_use_case.dtos.listar_categorias_input_dto import ListarCategoriasInputDTO
from finanzas.application.shared.dtos.categoria_listada_output_dto import CategoriaListadaOutputDTO


class IListarCategoriasUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarCategoriasInputDTO) -> list[CategoriaListadaOutputDTO]: ...
