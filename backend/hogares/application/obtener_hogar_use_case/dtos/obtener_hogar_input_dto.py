# hogares/application/obtener_hogar_use_case/dtos/obtener_hogar_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerHogarInputDTO:
    usuario_id: int
    hogar_id: int
