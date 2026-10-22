# finanzas/application/eliminar_categoria_use_case/eliminar_categoria_use_case.py (módulo 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.eliminar_categoria_use_case.dtos.eliminar_categoria_input_dto import (
    EliminarCategoriaInputDTO,
)
from finanzas.application.eliminar_categoria_use_case.i_eliminar_categoria_use_case import (
    IEliminarCategoriaUseCase,
)
from finanzas.domain.events.categorias_cambiadas_event import CategoriasCambiadasEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository


class EliminarCategoriaUseCase(IEliminarCategoriaUseCase):
    """Sus subcategorías se borran con ella y sus movimientos se quedan sin categoría (lo hace la BD:
    CASCADE y SET_NULL; los avisos y los eventos de esos movimientos los publican los receivers de
    pre_delete / post_delete de Categoria: finanzas/infrastructure/signals/receivers.py y eventos/receptores.py)."""

    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, categorias: ICategoriaCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.categorias, self.eventos, self.uow = categorias, eventos, uow

    def ejecutar(self, entrada: EliminarCategoriaInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            categoria = self.categorias.obtener(entrada.hogar_id, entrada.categoria_id)
            self.categorias.eliminar(categoria)
            self.eventos.publicar(CategoriasCambiadasEvent(entrada.hogar_id))
