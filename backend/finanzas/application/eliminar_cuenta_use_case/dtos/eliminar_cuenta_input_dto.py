# finanzas/application/eliminar_cuenta_use_case/dtos/eliminar_cuenta_input_dto.py (ejercicio 1 del módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class EliminarCuentaInputDTO:
    hogar_id: int
    actor: Actor
    cuenta_id: int
