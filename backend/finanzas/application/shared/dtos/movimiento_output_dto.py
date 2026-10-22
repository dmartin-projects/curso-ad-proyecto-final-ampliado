# finanzas/application/shared/dtos/movimiento_output_dto.py — lo que devuelven los use cases de un movimiento
# (módulo 87)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from finanzas.domain.bo.movimiento import Movimiento


@dataclass(frozen=True, slots=True)
class MovimientoOutputDTO:
    """Datos planos (tipos de Python, no value objects): quien lo recibe no necesita conocer el dominio."""

    id: int
    hogar_id: int
    cuenta_id: int
    fecha: date
    importe: Decimal
    concepto: str
    categoria_id: int | None
    comercio_id: int | None
    etiquetas: tuple[str, ...]
    notas: str
    origen: str
    revisado: bool

    @classmethod
    def desde_bo(cls, m: Movimiento) -> "MovimientoOutputDTO":
        return cls(
            id=m.id,
            hogar_id=m.hogar_id,
            cuenta_id=m.cuenta_id,
            fecha=m.fecha,
            importe=m.importe.cantidad,
            concepto=m.concepto,
            categoria_id=m.categoria_id,
            comercio_id=m.comercio_id,
            etiquetas=tuple(m.etiquetas),
            notas=m.notas,
            origen=str(m.origen),
            revisado=m.revisado,
        )
