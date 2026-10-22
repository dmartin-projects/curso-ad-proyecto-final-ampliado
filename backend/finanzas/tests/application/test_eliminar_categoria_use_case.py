"""EliminarCategoriaUseCase (y ReordenarCategoriasUseCase) con los fakes (módulo 87)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from finanzas.application.eliminar_categoria_use_case.dtos.eliminar_categoria_input_dto import (
    EliminarCategoriaInputDTO,
)
from finanzas.application.reordenar_categorias_use_case.dtos.reordenar_categorias_input_dto import (
    ReordenarCategoriasInputDTO,
)
from finanzas.tests.fakes.mundo import HOGAR, actor


def test_eliminar_borra_las_hijas_y_reordenar(mundo):
    a, b = mundo.categoria("A"), mundo.categoria("B")
    mundo.categoria("A1", padre=a)
    mundo.reordenar.ejecutar(ReordenarCategoriasInputDTO(HOGAR, actor(), (b.id, a.id)))
    assert [c.nombre for c in mundo.categorias.del_hogar(HOGAR) if c.es_raiz] == ["B", "A"]
    with pytest.raises(SinPermisoException):
        mundo.eliminar_categoria.ejecutar(EliminarCategoriaInputDTO(HOGAR, actor(Rol.LECTOR), a.id))
    mundo.eliminar_categoria.ejecutar(EliminarCategoriaInputDTO(HOGAR, actor(), a.id))
    assert [c.nombre for c in mundo.categorias.del_hogar(HOGAR)] == ["B"]
