# finanzas/application/registrar_movimiento_use_case/dtos/registrar_movimiento_input_dto.py (módulos 87 y 88)
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from core.domain.vo.actor import Actor
from finanzas.domain.enums.origen import Origen


@dataclass(frozen=True)
class RegistrarMovimientoInputDTO:
    hogar_id: int
    actor: Actor
    cuenta_id: int
    fecha: date
    importe: Decimal
    concepto: str
    categoria_id: int | None = None
    etiquetas: list[str] = field(default_factory=list)
    notas: str = ""
    revisado: bool = True
    origen: Origen = Origen.MANUAL  # confirmar un ticket sin gasto lo registra una persona, pero es de ticket
