"""Módulo 96: un prompt es código: sus huecos se rellenan todos, y solo esos."""

import pytest

from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt

SALUDO = PlantillaDePrompt("saludo", "1", "Hola, {nombre}. Hoy es {hoy}.")


def test_rellena_los_huecos():
    assert SALUDO.campos == {"nombre", "hoy"}
    assert SALUDO.rellenar(nombre="Ana", hoy="jueves") == "Hola, Ana. Hoy es jueves."


@pytest.mark.parametrize(
    "valores, error",
    [
        ({"nombre": "Ana"}, r"faltan \['hoy'\], sobran \[\]"),
        ({"nombre": "Ana", "hoy": "x", "zona": "UTC"}, r"sobran \['zona'\]"),
    ],
)
def test_un_hueco_sin_valor_o_un_valor_sin_hueco_es_un_error(valores, error):
    with pytest.raises(ValueError, match=error):
        SALUDO.rellenar(**valores)


def test_la_huella_cambia_con_el_texto_no_con_la_version():
    assert SALUDO.huella == PlantillaDePrompt("saludo", "2", SALUDO.texto).huella
    assert SALUDO.huella != PlantillaDePrompt("saludo", "1", SALUDO.texto + " ").huella
