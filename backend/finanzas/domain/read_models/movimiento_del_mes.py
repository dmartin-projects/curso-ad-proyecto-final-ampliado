# finanzas/domain/read_models/movimiento_del_mes.py — los movimientos de un mes, para el informe (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class MovimientoDelMes:
    """Una línea del informe mensual en PDF (módulo 78): con los nombres, no con ids."""

    id: int
    fecha: date
    concepto: str
    importe: Decimal
    cuenta: str
    categoria_id: int | None
    categoria: str | None  # como la enseña la app: «Padre › Hija» si es una subcategoría
