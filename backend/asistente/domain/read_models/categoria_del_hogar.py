# asistente/domain/read_models/categoria_del_hogar.py (módulo 95)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CategoriaDelHogar:
    id: int
    nombre: str
    padre: str | None  # el nombre de su categoría principal, si es una subcategoría
    es_ingreso: bool
