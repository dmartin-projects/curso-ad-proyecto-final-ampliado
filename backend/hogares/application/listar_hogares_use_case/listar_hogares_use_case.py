# hogares/application/listar_hogares_use_case/listar_hogares_use_case.py (módulo 88)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from hogares.application.listar_hogares_use_case.dtos.listar_hogares_input_dto import ListarHogaresInputDTO
from hogares.application.listar_hogares_use_case.i_listar_hogares_use_case import IListarHogaresUseCase
from hogares.application.shared.dtos.hogar_listado_output_dto import HogarListadoOutputDTO
from hogares.domain.repositories.i_hogar_query_service import IHogarQueryService
from hogares.domain.repositories.queries.hogares_query import HogaresQuery


class ListarHogaresUseCase(IListarHogaresUseCase):
    """Los hogares de quien pregunta. Sin rol_minimo: no es una operación DENTRO de un hogar."""

    def __init__(self, *, hogares: IHogarQueryService):
        self.hogares = hogares

    def ejecutar(self, entrada: ListarHogaresInputDTO) -> PaginaOutputDTO[HogarListadoOutputDTO]:
        pagina = self.hogares.listar(HogaresQuery(entrada.usuario_id, entrada.orden, entrada.paginacion))
        return PaginaOutputDTO.desde_pagina(pagina, HogarListadoOutputDTO.desde_read_model)
