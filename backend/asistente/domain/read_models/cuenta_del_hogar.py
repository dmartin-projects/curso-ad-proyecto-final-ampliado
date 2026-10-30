# asistente/domain/read_models/cuenta_del_hogar.py — una cuenta del hogar, para el asistente (módulo 97)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CuentaDelHogar:
    """Sin el IBAN: el modelo no lo necesita, y un dato que no viaja no se puede filtrar (módulo 102)."""

    id: int
    nombre: str
    tipo: str
    activa: bool
    saldo: Decimal
