# importaciones/domain/repositories/queries/filas_query.py (módulo 88)
from dataclasses import dataclass, field

from core.domain.repositories.queries.paginacion import Paginacion


@dataclass(frozen=True, slots=True)
class FilasQuery:
    importacion_id: int
    accion: str | None = None  # crear | duplicada | conciliar; cualquier otra cosa, todas
    paginacion: Paginacion = field(default_factory=Paginacion)
