# finanzas/application/shared/dtos/presupuesto_con_gastado_output_dto.py (módulo 87)
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal

from finanzas.domain.read_models.presupuesto_con_gastado import PresupuestoConGastado


@dataclass(frozen=True, slots=True)
class PresupuestoConGastadoOutputDTO:
    id: int
    categoria_id: int
    mes: date  # día 1
    importe: Decimal
    gastado: Decimal  # negativo: son gastos

    @classmethod
    def desde_read_model(cls, rm: PresupuestoConGastado) -> "PresupuestoConGastadoOutputDTO":
        return cls(**asdict(rm))  # los mismos campos: el read model es del dominio; el OutputDTO, del use case
