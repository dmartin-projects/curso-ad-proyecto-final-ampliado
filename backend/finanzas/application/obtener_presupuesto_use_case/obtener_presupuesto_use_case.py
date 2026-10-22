# finanzas/application/obtener_presupuesto_use_case/obtener_presupuesto_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from finanzas.application.obtener_presupuesto_use_case.dtos.obtener_presupuesto_input_dto import (
    ObtenerPresupuestoInputDTO,
)
from finanzas.application.obtener_presupuesto_use_case.i_obtener_presupuesto_use_case import IObtenerPresupuestoUseCase
from finanzas.application.shared.dtos.presupuesto_con_gastado_output_dto import PresupuestoConGastadoOutputDTO
from finanzas.domain.repositories.i_presupuesto_query_service import IPresupuestoQueryService


class ObtenerPresupuestoUseCase(IObtenerPresupuestoUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, presupuestos: IPresupuestoQueryService):
        self.presupuestos = presupuestos

    def ejecutar(self, entrada: ObtenerPresupuestoInputDTO) -> PresupuestoConGastadoOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leido = self.presupuestos.detalle(entrada.hogar_id, entrada.presupuesto_id)
        return None if leido is None else PresupuestoConGastadoOutputDTO.desde_read_model(leido)
