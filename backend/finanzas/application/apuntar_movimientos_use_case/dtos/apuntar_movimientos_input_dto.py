# finanzas/application/apuntar_movimientos_use_case/dtos/apuntar_movimientos_input_dto.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.actor import Actor
from finanzas.application.apuntar_movimientos_use_case.dtos.movimiento_apuntado_input_dto import (
    MovimientoApuntadoInputDTO,
)
from finanzas.domain.enums.origen import Origen


@dataclass(frozen=True)
class ApuntarMovimientosInputDTO:
    hogar_id: int
    actor: Actor  # normalmente Actor.sistema(en_nombre_de=quien subió el ticket o el extracto)
    cuenta_id: int
    origen: Origen
    movimientos: tuple[MovimientoApuntadoInputDTO, ...]
