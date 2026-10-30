from dataclasses import dataclass

from core.domain.vo.actor import Actor


@dataclass(frozen=True)
class PedirAnalisisInputDTO:
    hogar_id: int
    actor: Actor
    tarea: str  # lo genera el cliente (un UUID): así escucha los avisos ANTES de pedirlo
    mes: str | None = None  # AAAA-MM; sin él, el mes en curso del hogar
