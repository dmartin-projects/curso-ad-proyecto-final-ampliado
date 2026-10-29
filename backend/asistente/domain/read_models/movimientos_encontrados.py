# asistente/domain/read_models/movimientos_encontrados.py — el resultado de una búsqueda: los totales y unos pocos (módulo 95)
from dataclasses import dataclass
from decimal import Decimal

from asistente.domain.read_models.movimiento_encontrado import MovimientoEncontrado


@dataclass(frozen=True, slots=True)
class MovimientosEncontrados:
    total: int  # TODOS los que cumplen el filtro
    gastos: Decimal  # la suma de TODOS los gastos que lo cumplen (en positivo)
    ingresos: Decimal
    primeros: tuple[MovimientoEncontrado, ...]  # los más recientes, como ejemplo
