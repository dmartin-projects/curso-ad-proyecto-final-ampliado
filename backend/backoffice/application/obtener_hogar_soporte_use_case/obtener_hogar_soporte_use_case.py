# backoffice/application/obtener_hogar_soporte_use_case/obtener_hogar_soporte_use_case.py (módulo 88)
from backoffice.application.obtener_hogar_soporte_use_case.dtos.obtener_hogar_soporte_input_dto import (
    ObtenerHogarSoporteInputDTO,
)
from backoffice.application.obtener_hogar_soporte_use_case.i_obtener_hogar_soporte_use_case import (
    IObtenerHogarSoporteUseCase,
)
from backoffice.application.shared.dtos.hogar_soporte_output_dto import HogarSoporteOutputDTO
from backoffice.domain.repositories.i_hogar_soporte_query_service import IHogarSoporteQueryService


class ObtenerHogarSoporteUseCase(IObtenerHogarSoporteUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, hogares: IHogarSoporteQueryService):
        self.hogares = hogares

    def ejecutar(self, entrada: ObtenerHogarSoporteInputDTO) -> HogarSoporteOutputDTO | None:
        leido = self.hogares.detalle(entrada.hogar_id)
        return None if leido is None else HogarSoporteOutputDTO.desde_read_model(leido)
