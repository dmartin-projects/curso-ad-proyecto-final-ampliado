# informes/domain/read_models/informe_listado.py (módulo 88)
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class InformeListado:
    id: int
    mes: date  # día 1
    archivo: str
    tamano: int
    generado_por_id: int | None
    creado: datetime
    actualizado: datetime
