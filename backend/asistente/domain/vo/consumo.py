# asistente/domain/vo/consumo.py — lo que ha gastado UNA persona con UN modelo en una pregunta (módulo 98)
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from asistente.domain.enums.canal_de_consumo import CanalDeConsumo
from asistente.domain.vo.uso import Uso


@dataclass(frozen=True, slots=True)
class Consumo:
    """Una fila del libro de cuentas del asistente. Por modelo, porque con la reserva (módulo 94) una pregunta puede
    pasar por dos, y no cuestan lo mismo. El coste se calcula y se GUARDA al apuntarlo: si el proveedor cambia los
    precios, lo de ayer costó lo que costó. None si el modelo no tiene precio (mejor "desconocido" que inventado)."""

    usuario_id: int
    hogar_id: int
    canal: CanalDeConsumo
    modelo: str
    uso: Uso
    coste: Decimal | None
    momento: datetime
    conversacion_id: int | None = None
