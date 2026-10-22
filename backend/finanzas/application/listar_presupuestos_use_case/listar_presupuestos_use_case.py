# finanzas/application/listar_presupuestos_use_case/listar_presupuestos_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from finanzas.application.listar_presupuestos_use_case.dtos.listar_presupuestos_input_dto import (
    ListarPresupuestosInputDTO,
)
from finanzas.application.listar_presupuestos_use_case.i_listar_presupuestos_use_case import IListarPresupuestosUseCase
from finanzas.application.shared.dtos.presupuesto_con_gastado_output_dto import PresupuestoConGastadoOutputDTO
from finanzas.domain.repositories.i_presupuesto_query_service import IPresupuestoQueryService
from finanzas.domain.repositories.queries.presupuestos_query import PresupuestosQuery


class ListarPresupuestosUseCase(IListarPresupuestosUseCase):
    """Un use case de CONSULTA: sin transacción ni eventos; pide al query service y traduce a OutputDTOs."""

    rol_minimo = Rol.LECTOR

    def __init__(self, *, presupuestos: IPresupuestoQueryService):
        self.presupuestos = presupuestos

    def ejecutar(self, entrada: ListarPresupuestosInputDTO) -> list[PresupuestoConGastadoOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        leidos = self.presupuestos.listar(PresupuestosQuery(entrada.hogar_id, entrada.mes, entrada.orden))
        return [PresupuestoConGastadoOutputDTO.desde_read_model(p) for p in leidos]
