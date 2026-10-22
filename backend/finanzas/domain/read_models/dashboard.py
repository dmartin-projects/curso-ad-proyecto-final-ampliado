# finanzas/domain/read_models/dashboard.py — el resumen de un mes, tal como se lee (módulos 77 y 87)
#
# Un read model: datos planos, sin comportamiento ni ORM. Lo devuelve el query service del dashboard
# (IDashboardQueryService) y lo traduce a su OutputDTO el use case de consulta. Vive en el dominio porque la
# interfaz que lo devuelve vive en el dominio, y el dominio no puede importar application.
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from finanzas.domain.read_models.categoria_del_mes import CategoriaDelMes
from finanzas.domain.read_models.comercio_del_mes import ComercioDelMes
from finanzas.domain.read_models.dia_del_mes import DiaDelMes
from finanzas.domain.read_models.mes_en_resumen import MesEnResumen
from finanzas.domain.read_models.presupuesto_del_mes import PresupuestoDelMes


@dataclass(frozen=True, slots=True)
class Dashboard:
    mes: date  # día 1: es lo que esperan el serializer (formato AAAA-MM) y el filtro |date de las plantillas
    gastos: Decimal
    ingresos: Decimal
    balance: Decimal
    num_movimientos: int
    gastos_mes_anterior: Decimal
    variacion: Decimal | None
    por_categoria: list[CategoriaDelMes]
    acumulado: list[DiaDelMes]
    evolucion: list[MesEnResumen]
    top_comercios: list[ComercioDelMes]
    presupuestos: list[PresupuestoDelMes]
    pendientes_revision: int
