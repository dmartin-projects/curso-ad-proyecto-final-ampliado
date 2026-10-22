# importaciones/application/listar_importaciones_use_case/i_listar_importaciones_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from importaciones.application.listar_importaciones_use_case.dtos.listar_importaciones_input_dto import (
    ListarImportacionesInputDTO,
)
from importaciones.application.shared.dtos.importacion_listada_output_dto import ImportacionListadaOutputDTO


class IListarImportacionesUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarImportacionesInputDTO) -> PaginaOutputDTO[ImportacionListadaOutputDTO]: ...
