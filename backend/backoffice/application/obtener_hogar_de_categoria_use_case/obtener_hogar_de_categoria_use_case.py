# backoffice/application/obtener_hogar_de_categoria_use_case/obtener_hogar_de_categoria_use_case.py (módulo 88)
from backoffice.application.obtener_hogar_de_categoria_use_case.dtos.obtener_hogar_de_categoria_input_dto import (
    ObtenerHogarDeCategoriaInputDTO,
)
from backoffice.application.obtener_hogar_de_categoria_use_case.i_obtener_hogar_de_categoria_use_case import (
    IObtenerHogarDeCategoriaUseCase,
)
from backoffice.domain.repositories.i_movimiento_soporte_query_service import IMovimientoSoporteQueryService


class ObtenerHogarDeCategoriaUseCase(IObtenerHogarDeCategoriaUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, movimientos: IMovimientoSoporteQueryService):
        self.movimientos = movimientos

    def ejecutar(self, entrada: ObtenerHogarDeCategoriaInputDTO) -> int | None:
        return self.movimientos.hogar_de_categoria(entrada.categoria_id)
