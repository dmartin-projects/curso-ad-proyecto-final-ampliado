# importaciones/application/listar_filas_importacion_use_case/i_listar_filas_importacion_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from importaciones.application.listar_filas_importacion_use_case.dtos.listar_filas_importacion_input_dto import (
    ListarFilasImportacionInputDTO,
)
from importaciones.application.shared.dtos.fila_listada_output_dto import FilaListadaOutputDTO


class IListarFilasImportacionUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarFilasImportacionInputDTO) -> PaginaOutputDTO[FilaListadaOutputDTO] | None: ...
