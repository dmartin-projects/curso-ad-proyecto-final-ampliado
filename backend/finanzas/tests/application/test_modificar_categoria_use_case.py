"""ModificarCategoriaUseCase con los fakes (módulo 87)."""

from finanzas.application.modificar_categoria_use_case.dtos.modificar_categoria_input_dto import (
    ModificarCategoriaInputDTO,
)
from finanzas.tests.fakes.mundo import HOGAR, actor


def test_mover_a_la_raiz_y_renombrar(mundo):
    hogar = mundo.categoria("Hogar")
    luz = mundo.categoria("Luz", padre=hogar)
    entrada = ModificarCategoriaInputDTO(HOGAR, actor(), luz.id, {"padre_id": None, "nombre": "Electricidad"})
    mundo.modificar_categoria.ejecutar(entrada)
    guardada = mundo.categorias.obtener(HOGAR, luz.id)
    assert (guardada.padre_id, guardada.nombre) == (None, "Electricidad")
