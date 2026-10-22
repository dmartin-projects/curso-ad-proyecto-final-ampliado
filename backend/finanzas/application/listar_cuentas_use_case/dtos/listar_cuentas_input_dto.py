# finanzas/application/listar_cuentas_use_case/dtos/listar_cuentas_input_dto.py (módulo 87)
from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ListarCuentasInputDTO:
    hogar_id: int
    actor: Actor
    orden: tuple[str, ...] = ()
