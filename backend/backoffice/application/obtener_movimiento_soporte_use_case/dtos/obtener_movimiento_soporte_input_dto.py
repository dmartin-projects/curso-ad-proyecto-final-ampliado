# backoffice/application/obtener_movimiento_soporte_use_case/dtos/obtener_movimiento_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerMovimientoSoporteInputDTO:
    movimiento_id: int
