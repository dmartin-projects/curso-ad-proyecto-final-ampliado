# asistente/domain/read_models/resumen_del_mes.py — lo que el asistente lee del dashboard de un mes (módulo 94)
#
# Un read model del asistente, en sus palabras: el adapter hacia finanzas (infrastructure/finanzas/) traduce el
# DashboardOutputDTO de finanzas a esto. Si mañana finanzas cambia su DTO, cambia el adapter; las tools, no.
from dataclasses import dataclass
from decimal import Decimal

from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from core.domain.vo.mes import Mes


@dataclass(frozen=True, slots=True)
class ResumenDelMes:
    mes: Mes
    gastos: Decimal  # en positivo
    ingresos: Decimal
    balance: Decimal
    num_movimientos: int
    gastos_mes_anterior: Decimal
    variacion: Decimal | None  # % frente al mes anterior; None si el anterior no tuvo gastos
    por_categoria: tuple[GastoDeCategoria, ...]
    pendientes_revision: int
