# importaciones/domain/read_models/importacion_listada.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ImportacionListada:
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
