# backoffice/application/obtener_hogar_soporte_use_case/dtos/obtener_hogar_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerHogarSoporteInputDTO:
    hogar_id: int
