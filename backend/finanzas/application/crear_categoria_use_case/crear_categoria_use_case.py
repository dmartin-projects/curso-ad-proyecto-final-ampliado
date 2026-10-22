# finanzas/application/crear_categoria_use_case/crear_categoria_use_case.py (módulo 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.crear_categoria_use_case.dtos.crear_categoria_input_dto import CrearCategoriaInputDTO
from finanzas.application.crear_categoria_use_case.i_crear_categoria_use_case import ICrearCategoriaUseCase
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria
from finanzas.application.shared.dtos.categoria_output_dto import CategoriaOutputDTO
from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.events.categorias_cambiadas_event import CategoriasCambiadasEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository


class CrearCategoriaUseCase(ICrearCategoriaUseCase):
    rol_minimo = Rol.MIEMBRO  # quien apunta gastos puede organizar sus categorías

    def __init__(self, *, categorias: ICategoriaCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.categorias, self.eventos, self.uow = categorias, eventos, uow

    def ejecutar(self, entrada: CrearCategoriaInputDTO) -> CategoriaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        categoria = Categoria(
            hogar_id=entrada.hogar_id,
            nombre=entrada.nombre,
            color=entrada.color,
            icono=entrada.icono,
            orden=entrada.orden,
            es_ingreso=entrada.es_ingreso,
        )
        with self.uow:
            padre = None
            if entrada.padre_id is not None:
                padre = exigir_categoria(self.categorias, entrada.hogar_id, entrada.padre_id, "padre")
            categoria.colgar_de(padre, tiene_hijas=False)  # nueva: sin hijas
            self.categorias.guardar(categoria)
            self.eventos.publicar(CategoriasCambiadasEvent(entrada.hogar_id))
        return CategoriaOutputDTO.desde_bo(categoria)
