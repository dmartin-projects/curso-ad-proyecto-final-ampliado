# finanzas/application/listar_comercios_use_case/listar_comercios_use_case.py (módulo 87)
from core.application.dtos.pagina_output_dto import PaginaOutputDTO
from finanzas.application.listar_comercios_use_case.dtos.comercio_listado_output_dto import ComercioListadoOutputDTO
from finanzas.application.listar_comercios_use_case.dtos.listar_comercios_input_dto import ListarComerciosInputDTO
from finanzas.application.listar_comercios_use_case.i_listar_comercios_use_case import IListarComerciosUseCase
from finanzas.domain.repositories.i_comercio_query_service import IComercioQueryService
from finanzas.domain.repositories.queries.comercios_query import ComerciosQuery


class ListarComerciosUseCase(IListarComerciosUseCase):
    """Un use case de CONSULTA: sin transacción ni eventos; pide al query service y traduce a OutputDTOs.

    Sin rol: los comercios son de todos los hogares y basta con haber iniciado sesión (lo exige la view).
    """

    def __init__(self, *, comercios: IComercioQueryService):
        self.comercios = comercios

    def ejecutar(self, entrada: ListarComerciosInputDTO) -> PaginaOutputDTO[ComercioListadoOutputDTO]:
        pagina = self.comercios.listar(ComerciosQuery(entrada.busqueda, entrada.paginacion))
        return PaginaOutputDTO.desde_pagina(pagina, ComercioListadoOutputDTO.desde_read_model)
