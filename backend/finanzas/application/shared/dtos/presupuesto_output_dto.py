# finanzas/application/shared/dtos/presupuesto_output_dto.py (módulo 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from finanzas.domain.bo.presupuesto import Presupuesto


@dataclass(frozen=True, slots=True)
class PresupuestoOutputDTO:
    id: int
    hogar_id: int
    categoria_id: int
    mes: date  # día 1
    importe: Decimal
    alerta_enviada: bool

    @classmethod
    def desde_bo(cls, p: Presupuesto) -> "PresupuestoOutputDTO":
        return cls(
            id=p.id,
            hogar_id=p.hogar_id,
            categoria_id=p.categoria_id,
            mes=p.mes.inicio,
            importe=p.importe.cantidad,
            alerta_enviada=p.alerta_enviada,
        )
