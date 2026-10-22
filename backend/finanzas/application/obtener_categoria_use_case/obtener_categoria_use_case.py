# finanzas/application/obtener_categoria_use_case/obtener_categoria_use_case.py (módulo 87)
from core.domain.enums.rol import Rol
from finanzas.application.obtener_categoria_use_case.dtos.obtener_categoria_input_dto import ObtenerCategoriaInputDTO
from finanzas.application.obtener_categoria_use_case.i_obtener_categoria_use_case import IObtenerCategoriaUseCase
from finanzas.application.shared.dtos.categoria_listada_output_dto import CategoriaListadaOutputDTO
from finanzas.domain.repositories.i_categoria_query_service import ICategoriaQueryService


class ObtenerCategoriaUseCase(IObtenerCategoriaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, categorias: ICategoriaQueryService):
        self.categorias = categorias

    def ejecutar(self, entrada: ObtenerCategoriaInputDTO) -> CategoriaListadaOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leida = self.categorias.detalle(entrada.hogar_id, entrada.categoria_id)
        return None if leida is None else CategoriaListadaOutputDTO.desde_read_model(leida)
