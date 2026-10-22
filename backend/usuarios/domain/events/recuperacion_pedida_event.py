# usuarios/domain/events/recuperacion_pedida_event.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class RecuperacionPedidaEvent:
    usuario_id: int
    enlace: str
