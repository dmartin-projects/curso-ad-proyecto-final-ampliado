# finanzas/domain/read_models/categoria_listada.py (módulo 87)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CategoriaListada:
    id: int
    nombre: str
    padre_id: int | None
    color: str
    icono: str
    orden: int
    es_ingreso: bool
