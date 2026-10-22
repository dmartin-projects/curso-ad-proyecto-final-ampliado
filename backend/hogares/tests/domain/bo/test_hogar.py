"""El hogar (módulo 88): sus reglas, sin base de datos."""

import pytest

from hogares.domain.bo.hogar import Hogar
from hogares.domain.exceptions.zona_horaria_no_valida_exception import ZonaHorariaNoValidaException


@pytest.mark.parametrize("zona", ["Europa/Madrid", "Mars/Phobos", "", "../../etc/passwd"])
def test_la_zona_horaria_tiene_que_existir(zona):
    with pytest.raises(ZonaHorariaNoValidaException) as e:
        Hogar(nombre="Casa", zona_horaria=zona)
    assert e.value.campo == "zona_horaria"


def test_modificar_es_todo_o_nada():
    h = Hogar(nombre="Casa", zona_horaria="Atlantic/Canary")
    with pytest.raises(ZonaHorariaNoValidaException):
        h.modificar(nombre="Piso", zona_horaria="Canarias")
    assert h.nombre == "Casa"
    h.modificar(nombre=" Piso ", zona_horaria="America/Bogota")
    assert (h.nombre, h.zona_horaria) == ("Piso", "America/Bogota")
