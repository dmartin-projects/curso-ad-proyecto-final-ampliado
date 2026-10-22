# informes/domain/events/informe_pedido_event.py (módulo 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(frozen=True)
class InformePedidoEvent:
    """Generarlo en segundo plano: un PDF tarda segundos (módulo 78)."""

    hogar_id: int
    mes: Mes
    usuario_id: int | None
    enviar: bool
