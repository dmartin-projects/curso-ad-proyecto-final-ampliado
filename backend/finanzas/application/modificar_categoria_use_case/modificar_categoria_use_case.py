# finanzas/application/modificar_categoria_use_case/modificar_categoria_use_case.py (módulo 87)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from finanzas.application.modificar_categoria_use_case.dtos.modificar_categoria_input_dto import (
    ModificarCategoriaInputDTO,
)
from finanzas.application.modificar_categoria_use_case.i_modificar_categoria_use_case import (
    IModificarCategoriaUseCase,
)
from finanzas.application.shared.autorizacion_por_hogar import exigir_categoria
from finanzas.application.shared.dtos.categoria_output_dto import CategoriaOutputDTO
from finanzas.domain.events.categorias_cambiadas_event import CategoriasCambiadasEvent
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository


class ModificarCategoriaUseCase(IModificarCategoriaUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(self, *, categorias: ICategoriaCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.categorias, self.eventos, self.uow = categorias, eventos, uow

    def ejecutar(self, entrada: ModificarCategoriaInputDTO) -> CategoriaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        cambios = dict(entrada.cambios)
        with self.uow:
            categoria = self.categorias.obtener(entrada.hogar_id, entrada.categoria_id)
            if "padre_id" in cambios:
                padre_id = cambios.pop("padre_id")
                padre = None
                if padre_id is not None:
                    padre = exigir_categoria(self.categorias, entrada.hogar_id, padre_id, "padre")
                # tiene_hijas solo hace falta si va a colgar de otra: una consulta menos al renombrar
                categoria.colgar_de(padre, tiene_hijas=padre is not None and self.categorias.tiene_hijas(categoria.id))
            categoria.modificar(**cambios)
            self.categorias.guardar(categoria)
            self.eventos.publicar(CategoriasCambiadasEvent(entrada.hogar_id))
        return CategoriaOutputDTO.desde_bo(categoria)
