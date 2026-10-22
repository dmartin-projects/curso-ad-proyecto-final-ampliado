# finanzas/application/obtener_cuenta_use_case/dtos/obtener_cuenta_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerCuentaInputDTO:
    hogar_id: int
    actor: Actor
    cuenta_id: int
