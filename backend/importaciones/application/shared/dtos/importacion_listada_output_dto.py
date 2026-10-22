# importaciones/application/shared/dtos/importacion_listada_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from importaciones.domain.read_models.importacion_listada import ImportacionListada


@dataclass(frozen=True, slots=True)
class ImportacionListadaOutputDTO:
    id: int
    estado: str
    cuenta_id: int
    nombre_original: str
    formato: str
    total_filas: int
    procesadas: int
    progreso: int
    creados: int
    conciliados: int
    duplicados: int
    resumen: dict
    avisos: list
    error: str
    creado: datetime
    terminado_en: datetime | None

    @classmethod
    def desde_read_model(cls, rm: ImportacionListada) -> "ImportacionListadaOutputDTO":
        return cls(**{campo: getattr(rm, campo) for campo in cls.__dataclass_fields__})
