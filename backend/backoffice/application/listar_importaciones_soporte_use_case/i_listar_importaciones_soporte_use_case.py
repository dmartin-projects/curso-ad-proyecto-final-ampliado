# backoffice/application/listar_importaciones_soporte_use_case/i_listar_importaciones_soporte_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_importaciones_soporte_use_case.dtos.listar_importaciones_soporte_input_dto import (
    ListarImportacionesSoporteInputDTO,
)
from backoffice.application.shared.dtos.importacion_soporte_output_dto import ImportacionSoporteOutputDTO
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class IListarImportacionesSoporteUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarImportacionesSoporteInputDTO) -> PaginaOutputDTO[ImportacionSoporteOutputDTO]: ...
