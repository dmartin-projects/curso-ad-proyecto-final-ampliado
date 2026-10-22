# finanzas/domain/read_models/cuenta_con_saldo.py (módulo 87)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class CuentaConSaldo:
    id: int
    nombre: str
    tipo: str
    iban: str
    activa: bool
    saldo: Decimal
