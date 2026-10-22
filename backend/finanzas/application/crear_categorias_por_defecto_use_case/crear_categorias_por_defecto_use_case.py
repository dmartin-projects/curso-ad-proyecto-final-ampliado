# finanzas/application/crear_categorias_por_defecto_use_case/crear_categorias_por_defecto_use_case.py (módulo 87)
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from finanzas.application.crear_categorias_por_defecto_use_case.dtos.crear_categorias_por_defecto_input_dto import (
    CrearCategoriasPorDefectoInputDTO,
)
from finanzas.application.crear_categorias_por_defecto_use_case.i_crear_categorias_por_defecto_use_case import (
    ICrearCategoriasPorDefectoUseCase,
)
from finanzas.domain.repositories.i_categoria_command_repository import ICategoriaCommandRepository
from finanzas.domain.services.categorias_por_defecto import por_defecto


class CrearCategoriasPorDefectoUseCase(ICrearCategoriasPorDefectoUseCase):
    """Las categorías con las que nace un hogar (lo dispara hogar_creado). Lo pide el sistema, no una persona:
    no exige ningún rol."""

    def __init__(self, *, categorias: ICategoriaCommandRepository, uow: IUnidadDeTrabajo):
        self.categorias, self.uow = categorias, uow

    def ejecutar(self, entrada: CrearCategoriasPorDefectoInputDTO) -> int:
        with self.uow:
            raices, hijas_de = por_defecto(entrada.hogar_id)
            self.categorias.crear_varias(raices)  # un INSERT para todas: así ya tienen id
            hijas = []
            for raiz in raices:
                for hija in hijas_de.get(raiz.nombre, []) if not raiz.es_ingreso else []:
                    hija.padre_id = raiz.id
                    hijas.append(hija)
            self.categorias.crear_varias(hijas)
        return len(raices) + len(hijas)
