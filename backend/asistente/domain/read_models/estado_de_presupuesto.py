# asistente/domain/read_models/estado_de_presupuesto.py (módulo 95)
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class EstadoDePresupuesto:
    categoria: str
    importe: Decimal  # el presupuesto del mes
    gastado: Decimal
    porcentaje: int  # gastado sobre el presupuesto
