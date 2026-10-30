"""Módulo 97: las reglas de una conversación y una carpeta, sin base de datos."""

import pytest

from asistente.domain.bo.carpeta import Carpeta
from asistente.domain.bo.conversacion import Conversacion
from core.domain.exceptions.validacion_exception import ValidacionException


def test_el_titulo_automatico_no_pisa_el_de_la_persona():
    c = Conversacion(usuario_id=1, hogar_id=2)
    assert c.titular("Gasto de septiembre") and c.titulo == "Gasto de septiembre"
    c.renombrar("  Impuestos\n 2026 ")
    assert (c.titulo, c.titulo_manual) == ("Impuestos 2026", True)
    assert not c.titular("Otra cosa") and c.titulo == "Impuestos 2026"


@pytest.mark.parametrize("titulo", ["", "   ", "x" * 81])
def test_un_titulo_vacio_o_largo_no_vale(titulo):
    with pytest.raises(ValidacionException, match="entre 1 y 80") as e:
        Conversacion(1, 2).renombrar(titulo)
    assert e.value.campo == "titulo"


def test_el_automatico_se_recorta_a_80():
    c = Conversacion(1, 2)
    c.titular("x" * 120)
    assert len(c.titulo) == 80


def test_una_carpeta_con_nombre_limpio():
    assert Carpeta(1, 2, "  Viaje   a Lisboa ").nombre == "Viaje a Lisboa"
    with pytest.raises(ValidacionException, match="entre 1 y 60"):
        Carpeta(1, 2, "")
