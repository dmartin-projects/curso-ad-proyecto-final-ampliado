# backoffice/application/obtener_importacion_soporte_use_case/obtener_importacion_soporte_use_case.py (módulo 88)
from backoffice.application.obtener_importacion_soporte_use_case.dtos.obtener_importacion_soporte_input_dto import (
    ObtenerImportacionSoporteInputDTO,
)
from backoffice.application.obtener_importacion_soporte_use_case.i_obtener_importacion_soporte_use_case import (
    IObtenerImportacionSoporteUseCase,
)
from backoffice.application.shared.dtos.importacion_soporte_output_dto import ImportacionSoporteOutputDTO
from backoffice.domain.repositories.i_importacion_soporte_query_service import IImportacionSoporteQueryService


class ObtenerImportacionSoporteUseCase(IObtenerImportacionSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, importaciones: IImportacionSoporteQueryService):
        self.importaciones = importaciones

    def ejecutar(self, entrada: ObtenerImportacionSoporteInputDTO) -> ImportacionSoporteOutputDTO | None:
        leida = self.importaciones.detalle(entrada.importacion_id)
        return None if leida is None else ImportacionSoporteOutputDTO.desde_read_model(leida)
