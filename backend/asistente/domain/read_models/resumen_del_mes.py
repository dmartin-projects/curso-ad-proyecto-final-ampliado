# asistente/domain/read_models/resumen_del_mes.py — lo que el asistente lee del dashboard de un mes (módulos 94 y 95)
#
# Un read model del asistente, en sus palabras: el adapter hacia finanzas (infrastructure/finanzas/) traduce el
# DashboardOutputDTO de finanzas a esto. Si mañana finanzas cambia su DTO, cambia el adapter; las tools, no.
from dataclasses import dataclass
from decimal import Decimal

from asistente.domain.read_models.estado_de_presupuesto import EstadoDePresupuesto
from asistente.domain.read_models.gasto_de_categoria import GastoDeCategoria
from asistente.domain.read_models.gasto_de_comercio import GastoDeComercio
from asistente.domain.read_models.gasto_del_dia import GastoDelDia
from asistente.domain.read_models.mes_resumido import MesResumido
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
    # Módulo 95: el resto del dashboard, para las tools del catálogo
    top_comercios: tuple[GastoDeComercio, ...] = ()
    presupuestos: tuple[EstadoDePresupuesto, ...] = ()
    evolucion: tuple[MesResumido, ...] = ()  # los 12 meses que acaban en este
    por_dia: tuple[GastoDelDia, ...] = ()
