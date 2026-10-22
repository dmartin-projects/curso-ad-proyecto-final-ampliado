"""CrearCategoriaUseCase con los fakes (módulo 87)."""

import pytest

from finanzas.application.crear_categoria_use_case.dtos.crear_categoria_input_dto import CrearCategoriaInputDTO
from finanzas.application.modificar_categoria_use_case.dtos.modificar_categoria_input_dto import (
    ModificarCategoriaInputDTO,
)
from finanzas.domain.events.categorias_cambiadas_event import CategoriasCambiadasEvent
from finanzas.domain.exceptions.categoria_duplicada_exception import CategoriaDuplicadaException
from finanzas.domain.exceptions.categoria_no_encontrada_exception import CategoriaNoEncontradaException
from finanzas.domain.exceptions.demasiados_niveles_exception import DemasiadosNivelesException
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR, actor


def test_crear_subcategoria_y_avisar_al_dashboard(mundo):
    hogar = mundo.categoria("Hogar")
    luz = mundo.crear_categoria.ejecutar(CrearCategoriaInputDTO(HOGAR, actor(), "Luz", padre_id=hogar.id))
    assert mundo.categorias.obtener(HOGAR, luz.id).padre_id == hogar.id
    assert mundo.eventos.publicados == [CategoriasCambiadasEvent(HOGAR)]


def test_jerarquia_y_duplicados(mundo):
    hogar = mundo.categoria("Hogar")
    luz = mundo.categoria("Luz", padre=hogar)
    with pytest.raises(DemasiadosNivelesException):  # Hogar › Luz › Factura
        mundo.crear_categoria.ejecutar(CrearCategoriaInputDTO(HOGAR, actor(), "Factura", padre_id=luz.id))
    ocio = mundo.categoria("Ocio")
    with pytest.raises(DemasiadosNivelesException):  # Hogar tiene hijas: no puede colgar de Ocio
        mundo.modificar_categoria.ejecutar(ModificarCategoriaInputDTO(HOGAR, actor(), hogar.id, {"padre_id": ocio.id}))
    with pytest.raises(DemasiadosNivelesException):  # un ciclo
        mundo.modificar_categoria.ejecutar(ModificarCategoriaInputDTO(HOGAR, actor(), ocio.id, {"padre_id": ocio.id}))
    with pytest.raises(CategoriaDuplicadaException):
        mundo.crear_categoria.ejecutar(CrearCategoriaInputDTO(HOGAR, actor(), "Luz", padre_id=hogar.id))
    ajena = mundo.categoria("Ajena", hogar_id=OTRO_HOGAR)
    with pytest.raises(CategoriaNoEncontradaException) as e:
        mundo.crear_categoria.ejecutar(CrearCategoriaInputDTO(HOGAR, actor(), "X", padre_id=ajena.id))
    assert e.value.campo == "padre"
    assert mundo.eventos.publicados == []  # ninguno ha llegado a confirmarse
