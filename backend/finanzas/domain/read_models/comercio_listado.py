# finanzas/domain/read_models/comercio_listado.py (módulo 87)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ComercioListado:
    id: int
    nombre: str
