# finanzas/application/obtener_movimiento_use_case/obtener_movimiento_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from finanzas.application.obtener_movimiento_use_case.dtos.obtener_movimiento_input_dto import ObtenerMovimientoInputDTO
from finanzas.application.obtener_movimiento_use_case.i_obtener_movimiento_use_case import IObtenerMovimientoUseCase
from finanzas.application.shared.dtos.movimiento_listado_output_dto import MovimientoListadoOutputDTO
from finanzas.domain.repositories.i_movimiento_query_service import IMovimientoQueryService


class ObtenerMovimientoUseCase(IObtenerMovimientoUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, movimientos: IMovimientoQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ObtenerMovimientoInputDTO) -> MovimientoListadoOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leido = self.movimientos.detalle(entrada.hogar_id, entrada.movimiento_id)
        return None if leido is None else MovimientoListadoOutputDTO.desde_read_model(leido)
