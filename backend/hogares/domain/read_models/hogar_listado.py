# hogares/domain/read_models/hogar_listado.py (módulo 88)
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class HogarListado:
    """Un hogar visto por uno de sus miembros: con su rol en él y cuántos miembros tiene."""

    id: int
    nombre: str
    moneda: str
    zona_horaria: str
    mi_rol: str
    num_miembros: int
    creado: datetime
