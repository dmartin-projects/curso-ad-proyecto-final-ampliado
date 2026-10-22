# notificaciones/application/contar_no_leidas_use_case/dtos/contar_no_leidas_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ContarNoLeidasInputDTO:
    usuario_id: int
