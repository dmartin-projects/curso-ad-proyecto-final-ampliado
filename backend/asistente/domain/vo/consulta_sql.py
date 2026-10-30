# asistente/domain/vo/consulta_sql.py — "ver los datos": la consulta y su resultado, para la interfaz (módulo 101)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConsultaSQL:
    sql: str
    columnas: tuple[str, ...]
    filas: tuple[tuple, ...]
    recortado: bool
