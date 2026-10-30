from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class ObtenerEstadoInputDTO:
    hogar_id: int
    actor: Actor
