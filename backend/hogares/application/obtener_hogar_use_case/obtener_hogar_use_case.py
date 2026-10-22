# hogares/application/obtener_hogar_use_case/obtener_hogar_use_case.py (módulo 88)
from hogares.application.obtener_hogar_use_case.dtos.obtener_hogar_input_dto import ObtenerHogarInputDTO
from hogares.application.obtener_hogar_use_case.i_obtener_hogar_use_case import IObtenerHogarUseCase
from hogares.application.shared.dtos.hogar_listado_output_dto import HogarListadoOutputDTO
from hogares.domain.repositories.i_hogar_query_service import IHogarQueryService


class ObtenerHogarUseCase(IObtenerHogarUseCase):
    """None si no es uno de sus hogares: para quien pregunta, no existe."""

    def __init__(self, *, hogares: IHogarQueryService):
        self.hogares = hogares

    def ejecutar(self, entrada: ObtenerHogarInputDTO) -> HogarListadoOutputDTO | None:
        leido = self.hogares.detalle(entrada.usuario_id, entrada.hogar_id)
        return None if leido is None else HogarListadoOutputDTO.desde_read_model(leido)
