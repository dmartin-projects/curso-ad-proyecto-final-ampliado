# finanzas/application/obtener_totales_movimientos_use_case/dtos/totales_de_movimientos_output_dto.py (módulo 95)
from dataclasses import asdict, dataclass
from decimal import Decimal

from finanzas.domain.read_models.totales_de_movimientos import TotalesDeMovimientos


@dataclass(frozen=True, slots=True)
class TotalesDeMovimientosOutputDTO:
    num: int
    gastos: Decimal
    ingresos: Decimal

    @classmethod
    def desde_read_model(cls, rm: TotalesDeMovimientos) -> "TotalesDeMovimientosOutputDTO":
        return cls(**asdict(rm))
