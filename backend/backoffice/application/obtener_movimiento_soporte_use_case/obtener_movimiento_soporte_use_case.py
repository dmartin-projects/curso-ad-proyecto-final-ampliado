# backoffice/application/obtener_movimiento_soporte_use_case/obtener_movimiento_soporte_use_case.py (módulo 88)
from backoffice.application.obtener_movimiento_soporte_use_case.dtos.obtener_movimiento_soporte_input_dto import (
    ObtenerMovimientoSoporteInputDTO,
)
from backoffice.application.obtener_movimiento_soporte_use_case.i_obtener_movimiento_soporte_use_case import (
    IObtenerMovimientoSoporteUseCase,
)
from backoffice.application.shared.dtos.movimiento_soporte_output_dto import MovimientoSoporteOutputDTO
from backoffice.domain.repositories.i_movimiento_soporte_query_service import IMovimientoSoporteQueryService


class ObtenerMovimientoSoporteUseCase(IObtenerMovimientoSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, movimientos: IMovimientoSoporteQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ObtenerMovimientoSoporteInputDTO) -> MovimientoSoporteOutputDTO | None:
        leido = self.movimientos.detalle(entrada.movimiento_id)
        return None if leido is None else MovimientoSoporteOutputDTO.desde_read_model(leido)
