# backoffice/domain/read_models/importacion_soporte.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ImportacionSoporte:
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
