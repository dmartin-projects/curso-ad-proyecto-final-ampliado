# importaciones/application/obtener_importacion_use_case/obtener_importacion_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from importaciones.application.obtener_importacion_use_case.dtos.obtener_importacion_input_dto import (
    ObtenerImportacionInputDTO,
)
from importaciones.application.obtener_importacion_use_case.i_obtener_importacion_use_case import (
    IObtenerImportacionUseCase,
)
from importaciones.application.shared.dtos.importacion_listada_output_dto import ImportacionListadaOutputDTO
from importaciones.domain.repositories.i_importacion_query_service import IImportacionQueryService


class ObtenerImportacionUseCase(IObtenerImportacionUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, importaciones: IImportacionQueryService):
        self.importaciones = importaciones

    def ejecutar(self, entrada: ObtenerImportacionInputDTO) -> ImportacionListadaOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leida = self.importaciones.detalle(entrada.hogar_id, entrada.importacion_id)
        return None if leida is None else ImportacionListadaOutputDTO.desde_read_model(leida)
