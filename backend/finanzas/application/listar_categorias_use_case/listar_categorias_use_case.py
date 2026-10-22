# finanzas/application/listar_categorias_use_case/listar_categorias_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from finanzas.application.listar_categorias_use_case.dtos.listar_categorias_input_dto import ListarCategoriasInputDTO
from finanzas.application.listar_categorias_use_case.i_listar_categorias_use_case import IListarCategoriasUseCase
from finanzas.application.shared.dtos.categoria_listada_output_dto import CategoriaListadaOutputDTO
from finanzas.domain.repositories.i_categoria_query_service import ICategoriaQueryService
from finanzas.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery


class ListarCategoriasUseCase(IListarCategoriasUseCase):
    """Un use case de CONSULTA: sin transacción ni eventos; pide al query service y traduce a OutputDTOs."""

    rol_minimo = Rol.LECTOR

    def __init__(self, *, categorias: ICategoriaQueryService):
        self.categorias = categorias

    def ejecutar(self, entrada: ListarCategoriasInputDTO) -> list[CategoriaListadaOutputDTO]:
        entrada.actor.exigir(self.rol_minimo)
        leidas = self.categorias.listar(ListadoDelHogarQuery(entrada.hogar_id, entrada.orden))
        return [CategoriaListadaOutputDTO.desde_read_model(c) for c in leidas]
