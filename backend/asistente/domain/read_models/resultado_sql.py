# asistente/domain/read_models/resultado_sql.py (módulo 101)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResultadoSQL:
    columnas: tuple[str, ...]
    filas: tuple[tuple, ...]  # como mucho ASISTENTE_SQL_FILAS
    recortado: bool  # había más filas
    ms: int
