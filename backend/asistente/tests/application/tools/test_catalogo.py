"""Módulos 95, 97 y 99: reglas que cumple TODO el catálogo. Una tool nueva que se las salte rompe este test, no la seguridad."""

import pytest

from asistente.domain.exceptions.tool_exception import ToolException
from asistente.tests.fakes.mundo import Mundo

CATALOGO = Mundo().catalogo(chat=True)  # el del chat: el de consulta y las de su canal


def test_veinte_tools_sin_nombres_repetidos():  # 11 del 95, 2 de sus ejercicios, 5 del 97, recordar y olvidar (99)
    nombres = [t.nombre for t in CATALOGO]
    assert len(nombres) == len(set(nombres)) == 20


@pytest.mark.parametrize("tool", CATALOGO, ids=lambda t: t.nombre)
def test_ninguna_deja_al_modelo_elegir_hogar_ni_usuario(tool):
    campos = set(tool.Argumentos.model_fields)
    assert not campos & {"hogar_id", "hogar", "usuario_id", "usuario", "actor"}
    with pytest.raises(ToolException, match="hogar_id: Extra inputs are not permitted"):
        tool.validar('{"hogar_id": 2}')


@pytest.mark.parametrize("tool", CATALOGO, ids=lambda t: t.nombre)
def test_cada_una_dice_para_que_sirve_en_pocas_palabras(tool):
    assert 40 <= len(tool.descripcion) <= 320, tool.descripcion
    for nombre, campo in tool.Argumentos.model_fields.items():
        assert campo.description, f"{tool.nombre}.{nombre} sin descripción: el modelo solo sabe lo que dice el schema"
