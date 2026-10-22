# finanzas/application/apuntar_movimientos_use_case/dtos/movimiento_apuntado_input_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class MovimientoApuntadoInputDTO:
    """Un movimiento tal como lo trae un proceso. Lo que no sepa, lo completa finanzas."""

    fecha: date
    importe: Decimal
    concepto: str
    comercio: str = ""  # el nombre comercial, si quien apunta lo conoce (el ticket lo lee); si no, por el concepto
    nif: str = ""
    comercio_id: int | None = None  # ya resuelto (el seed)
    categoria_id: int | None = None  # ya elegida; si no, la habitual del hogar para ese comercio
    categoria_sugerida: str = ""  # la que propone otro (la IA del ticket) si el hogar aún no tiene costumbre
    huella: str = ""  # la fila del extracto del banco (importaciones)
    revisado: bool = True
