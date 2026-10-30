# asistente/application/consultar_cuota_use_case/dtos/consultar_cuota_input_dto.py (módulo 98)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ConsultarCuotaInputDTO:
    hogar_id: int
    actor: Actor
