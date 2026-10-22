# finanzas/application/obtener_dashboard_use_case/dtos/dashboard_output_dto.py (módulos 77 y 87)
#
# El contrato de application con quien lee el dashboard: la API (DashboardSerializer) y, en la Parte 7, las tools
# del agente. Tiene los mismos campos que el read model del dominio, y aun así es otra clase: el read model es lo
# que el dominio promete (IDashboardQueryService); el OutputDTO, lo que promete el use case a sus adapters.
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from finanzas.application.obtener_dashboard_use_case.dtos.categoria_del_mes_output_dto import CategoriaDelMesOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.comercio_del_mes_output_dto import ComercioDelMesOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.dia_del_mes_output_dto import DiaDelMesOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.mes_en_resumen_output_dto import MesEnResumenOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.presupuesto_del_mes_output_dto import (
    PresupuestoDelMesOutputDTO,
)


@dataclass(frozen=True, slots=True)
class DashboardOutputDTO:
    mes: date  # día 1: es lo que espera DashboardSerializer (formato AAAA-MM)
    gastos: Decimal
    ingresos: Decimal
    balance: Decimal
    num_movimientos: int
    gastos_mes_anterior: Decimal
    variacion: Decimal | None
    por_categoria: list[CategoriaDelMesOutputDTO]
    acumulado: list[DiaDelMesOutputDTO]
    evolucion: list[MesEnResumenOutputDTO]
    top_comercios: list[ComercioDelMesOutputDTO]
    presupuestos: list[PresupuestoDelMesOutputDTO]
    pendientes_revision: int
