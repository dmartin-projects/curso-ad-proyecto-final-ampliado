# finanzas/application/obtener_categoria_use_case/i_obtener_categoria_use_case.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.application.obtener_categoria_use_case.dtos.obtener_categoria_input_dto import ObtenerCategoriaInputDTO
from finanzas.application.shared.dtos.categoria_listada_output_dto import CategoriaListadaOutputDTO


class IObtenerCategoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerCategoriaInputDTO) -> CategoriaListadaOutputDTO | None: ...
