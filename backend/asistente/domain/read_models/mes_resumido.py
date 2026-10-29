# asistente/domain/read_models/mes_resumido.py (módulo 95)
from dataclasses import dataclass
from decimal import Decimal

from core.domain.vo.mes import Mes


@dataclass(frozen=True, slots=True)
class MesResumido:
    mes: Mes
    gastos: Decimal
    ingresos: Decimal
