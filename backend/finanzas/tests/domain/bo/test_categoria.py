"""El BO Categoria: dos niveles como mucho, sin base de datos (módulo 87)."""

import pytest

from finanzas.domain.bo.categoria import Categoria
from finanzas.domain.exceptions.color_no_valido_exception import ColorNoValidoException
from finanzas.domain.exceptions.demasiados_niveles_exception import DemasiadosNivelesException


def cat(nombre, id, padre_id=None):
    return Categoria(hogar_id=1, nombre=nombre, id=id, padre_id=padre_id)


def test_color_y_nombre():
    with pytest.raises(ColorNoValidoException):
        Categoria(hogar_id=1, nombre="X", color="rojo")
    assert Categoria(hogar_id=1, nombre="  Ocio ").nombre == "Ocio"


def test_dos_niveles_como_mucho():
    comida, fruta, ocio = cat("Comida", 1), cat("Fruta", 2, padre_id=1), cat("Ocio", 3)
    ocio.colgar_de(comida, tiene_hijas=False)
    assert ocio.padre_id == 1
    with pytest.raises(DemasiadosNivelesException):
        cat("Manzanas", 4).colgar_de(fruta, tiene_hijas=False)  # el padre ya es subcategoría
    with pytest.raises(DemasiadosNivelesException):
        comida.colgar_de(cat("Casa", 5), tiene_hijas=True)  # Comida tiene hijas: serían tres niveles
    with pytest.raises(DemasiadosNivelesException):
        comida.colgar_de(comida, tiene_hijas=False)  # un ciclo
    ocio.colgar_de(None, tiene_hijas=False)
    assert ocio.es_raiz
