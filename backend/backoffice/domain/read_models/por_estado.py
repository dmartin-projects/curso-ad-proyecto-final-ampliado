# backoffice/domain/read_models/por_estado.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PorEstado:
    clave: str
    total: int
