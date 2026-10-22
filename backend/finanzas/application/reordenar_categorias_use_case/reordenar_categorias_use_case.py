# finanzas/application/reordenar_categorias_use_case/reordenar_categorias_use_case.py (módulo 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.reordenar_categorias_use_case.dtos.reordenar_categorias_input_dto import (
    ReordenarCategoriasInputDTO,
)
from finanzas.application.reordenar_categorias_use_case.i_reordenar_categorias_use_case import (
    IReordenarCategoriasUseCase,
)
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.services.reordenar_categorias import reordenar


class ReordenarCategoriasUseCase(IReordenarCategoriasUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, categorias: ICategoriaCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.categorias, self.eventos, self.uow = categorias, eventos, uow

    def ejecutar(self, entrada: ReordenarCategoriasInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            cambiadas = reordenar(self.categorias.del_hogar(entrada.hogar_id), list(entrada.ids))
            self.categorias.guardar_orden(cambiadas)
            # sin evento, a propósito: el orden no cambia ningún número del dashboard
