# backoffice/application/shared/dtos/movimiento_soporte_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from backoffice.domain.read_models.movimiento_soporte import MovimientoSoporte


@dataclass(frozen=True, slots=True)
class MovimientoSoporteOutputDTO:
    id: int
    hogar_id: int
    fecha: date
    importe: Decimal
    concepto: str
    categoria_id: int | None
    categoria_nombre: str | None
    origen: str
    revisado: bool

    @classmethod
    def desde_read_model(cls, rm: MovimientoSoporte) -> "MovimientoSoporteOutputDTO":
        return cls(
            id=rm.id,
            hogar_id=rm.hogar_id,
            fecha=rm.fecha,
            importe=rm.importe,
            concepto=rm.concepto,
            categoria_id=rm.categoria_id,
            categoria_nombre=rm.categoria_nombre,
            origen=rm.origen,
            revisado=rm.revisado,
        )
