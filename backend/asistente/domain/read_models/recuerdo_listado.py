# asistente/domain/read_models/recuerdo_listado.py (módulo 99)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class RecuerdoListado:
    id: int
    texto: str
    creado: datetime
