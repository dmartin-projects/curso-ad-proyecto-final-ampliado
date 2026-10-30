"""Módulo 99, ejercicio 1: olvidar desde el chat, solo si las palabras identifican un recuerdo."""

import pytest

from asistente.application.tools.olvidar_tool import OlvidarTool
from asistente.domain.bo.recuerdo import Recuerdo
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.tests.fakes.mundo import ANA, HOGAR, contexto, reloj
from asistente.tests.fakes.recuerdo_repositorio_fake import RecuerdoRepositorioFake


@pytest.fixture
def recuerdos():
    r = RecuerdoRepositorioFake()
    for texto in ("La cuenta común es la de ING.", "La cuenta de ahorro es la de Openbank.", "No contar el alquiler."):
        r.guardar(Recuerdo(ANA, HOGAR, texto, reloj().ahora()))
    return r


def olvidar(recuerdos, texto: str) -> dict:
    tool = OlvidarTool(recuerdos=recuerdos, consultas=recuerdos)
    return tool.ejecutar(contexto(), tool.validar(f'{{"texto": "{texto}"}}'))


def test_sin_tildes_ni_mayusculas_y_solo_ese(recuerdos):
    assert olvidar(recuerdos, "cuenta comun ing") == {"olvidado": "La cuenta común es la de ING."}
    assert [r.texto for r in recuerdos.listar(ANA, HOGAR)] == [
        "La cuenta de ahorro es la de Openbank.",
        "No contar el alquiler.",
    ]


def test_si_hay_dudas_pregunta(recuerdos):
    with pytest.raises(ToolException, match="Hay varios"):
        olvidar(recuerdos, "cuenta")
    assert recuerdos.contar(ANA, HOGAR) == 3


def test_si_no_existe_dice_los_que_hay(recuerdos):
    with pytest.raises(ToolException, match="Ningún recuerdo contiene «BBVA».*alquiler"):
        olvidar(recuerdos, "BBVA")
