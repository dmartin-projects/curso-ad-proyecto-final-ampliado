# finanzas/application/obtener_dashboard_use_case/obtener_dashboard_use_case.py — un use case de CONSULTA (módulo 87)
#
# Lado de lectura de CQRS: usa un query service (nunca un command repository), no abre transacción y no publica
# nada. Su trabajo es exigir el rol y traducir el read model del dominio a su OutputDTO.
from dataclasses import asdict

from core.domain.enums.rol import Rol
from finanzas.application.obtener_dashboard_use_case.dtos.categoria_del_mes_output_dto import CategoriaDelMesOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.comercio_del_mes_output_dto import ComercioDelMesOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.dashboard_output_dto import DashboardOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.dia_del_mes_output_dto import DiaDelMesOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.mes_en_resumen_output_dto import MesEnResumenOutputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.obtener_dashboard_input_dto import ObtenerDashboardInputDTO
from finanzas.application.obtener_dashboard_use_case.dtos.presupuesto_del_mes_output_dto import (
    PresupuestoDelMesOutputDTO,
)
from finanzas.application.obtener_dashboard_use_case.i_obtener_dashboard_use_case import IObtenerDashboardUseCase
from finanzas.domain.read_models.dashboard import Dashboard
from finanzas.domain.repositories.i_dashboard_query_service import IDashboardQueryService
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery


class ObtenerDashboardUseCase(IObtenerDashboardUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, dashboard: IDashboardQueryService):
        self.dashboard = dashboard

    def ejecutar(self, entrada: ObtenerDashboardInputDTO) -> DashboardOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        return _a_output(self.dashboard.resumen(DashboardQuery(entrada.hogar_id, entrada.mes)))


def _a_output(d: Dashboard) -> DashboardOutputDTO:
    """Read model (dominio) → OutputDTO (application). Los mismos campos: se copian, sin lógica."""
    return DashboardOutputDTO(
        mes=d.mes,
        gastos=d.gastos,
        ingresos=d.ingresos,
        balance=d.balance,
        num_movimientos=d.num_movimientos,
        gastos_mes_anterior=d.gastos_mes_anterior,
        variacion=d.variacion,
        por_categoria=[CategoriaDelMesOutputDTO(**asdict(c)) for c in d.por_categoria],
        acumulado=[DiaDelMesOutputDTO(**asdict(x)) for x in d.acumulado],
        evolucion=[MesEnResumenOutputDTO(**asdict(m)) for m in d.evolucion],
        top_comercios=[ComercioDelMesOutputDTO(**asdict(c)) for c in d.top_comercios],
        presupuestos=[PresupuestoDelMesOutputDTO(**asdict(p)) for p in d.presupuestos],
        pendientes_revision=d.pendientes_revision,
    )
