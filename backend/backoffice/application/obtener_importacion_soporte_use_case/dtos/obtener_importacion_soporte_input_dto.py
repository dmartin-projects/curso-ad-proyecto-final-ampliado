# backoffice/application/obtener_importacion_soporte_use_case/dtos/obtener_importacion_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerImportacionSoporteInputDTO:
    importacion_id: int
