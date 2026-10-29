"""Módulo 94: qué ve el modelo de una tool y cómo se valida lo que manda."""

import pytest
from pydantic import Field

from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.tool_exception import ToolException


class Args(SinArgumentos):
    """Esta descripción no viaja: es para quien lee el código."""

    texto: str = Field(max_length=10, description="Lo que se busca")
    limite: int = Field(5, ge=1, le=20)
    categoria: str | None = Field(None, description="Opcional")


class Buscar(Tool):
    nombre, descripcion, Argumentos = "buscar", "Busca.", Args

    def ejecutar(self, contexto, args):
        return {}


def test_la_declaracion_sin_titulos_ni_docstring():
    d = Buscar().declaracion()
    assert (d.nombre, d.descripcion) == ("buscar", "Busca.")
    assert d.parametros == {
        "additionalProperties": False,
        "properties": {
            "texto": {"description": "Lo que se busca", "maxLength": 10, "type": "string"},
            "limite": {"default": 5, "maximum": 20, "minimum": 1, "type": "integer"},
            "categoria": {"description": "Opcional", "type": "string"},  # sin anyOf [string, null] ni default null
        },
        "required": ["texto"],
        "type": "object",
    }


def test_valida_y_aplica_los_valores_por_defecto():
    assert Buscar().validar('{"texto": "luz"}') == Args(texto="luz", limite=5)
    assert Buscar().validar('{"texto": "luz", "categoria": null}').categoria is None  # un null sigue valiendo


def test_sin_argumentos_es_un_objeto_vacio():
    class Hoy(Tool):
        nombre, descripcion = "hoy", "Sin argumentos."

        def ejecutar(self, contexto, args):
            return {}

    assert Hoy().validar("") == SinArgumentos()  # algunos modelos mandan "" en vez de "{}"
    assert Hoy().declaracion().parametros == {"additionalProperties": False, "properties": {}, "type": "object"}


@pytest.mark.parametrize(
    "argumentos, error",
    [
        ("{}", "texto: Field required"),
        ('{"texto": "luz", "limite": 50}', "limite: Input should be less than or equal to 20"),
        ('{"texto": "muy largo de verdad"}', "texto: String should have at most 10 characters"),
        ('{"texto": "luz", "hogar_id": 2}', "hogar_id: Extra inputs are not permitted"),
        ("[1, 2]", "argumentos: Input should be an object"),
    ],
)
def test_los_errores_en_una_linea_para_el_modelo(argumentos, error):
    with pytest.raises(ToolException, match=f"^Argumentos no válidos para buscar: {error}"):
        Buscar().validar(argumentos)
