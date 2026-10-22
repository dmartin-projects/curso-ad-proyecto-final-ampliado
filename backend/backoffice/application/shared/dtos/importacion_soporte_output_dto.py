# backoffice/application/shared/dtos/importacion_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime

from backoffice.domain.read_models.importacion_soporte import ImportacionSoporte


@dataclass(frozen=True, slots=True)
class ImportacionSoporteOutputDTO:
    id: int
    hogar_id: int
    hogar_nombre: str
    nombre_original: str
    estado: str
    progreso: int
    total_filas: int
    creados: int
    conciliados: int
    duplicados: int
    error: str
    creado: datetime

    @classmethod
    def desde_read_model(cls, rm: ImportacionSoporte) -> "ImportacionSoporteOutputDTO":
        return cls(
            id=rm.id,
            hogar_id=rm.hogar_id,
            hogar_nombre=rm.hogar_nombre,
            nombre_original=rm.nombre_original,
            estado=rm.estado,
            progreso=rm.progreso,
            total_filas=rm.total_filas,
            creados=rm.creados,
            conciliados=rm.conciliados,
            duplicados=rm.duplicados,
            error=rm.error,
            creado=rm.creado,
        )
