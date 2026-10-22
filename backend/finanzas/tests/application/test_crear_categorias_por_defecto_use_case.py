"""CrearCategoriasPorDefectoUseCase con los fakes (módulo 87)."""

from finanzas.application.crear_categorias_por_defecto_use_case.dtos.crear_categorias_por_defecto_input_dto import (
    CrearCategoriasPorDefectoInputDTO,
)
from finanzas.tests.fakes.mundo import HOGAR


def test_categorias_por_defecto(mundo):
    assert mundo.por_defecto.ejecutar(CrearCategoriasPorDefectoInputDTO(HOGAR)) == 22
    por_nombre = {c.nombre: c for c in mundo.categorias.del_hogar(HOGAR)}
    assert por_nombre["Luz"].padre_id == por_nombre["Hogar"].id
    assert por_nombre["Nómina"].es_ingreso and por_nombre["Nómina"].padre_id is None
    assert mundo.uow.confirmadas == 1
