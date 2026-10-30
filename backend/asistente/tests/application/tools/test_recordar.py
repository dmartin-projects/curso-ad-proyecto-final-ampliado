"""Módulo 99: la tool recordar. Pocos y cortos: viajan todos en cada pregunta."""

import pytest

from asistente.application.tools.recordar_tool import RecordarTool
from asistente.domain.bo.recuerdo import MAX_RECUERDOS
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.vo.recuerdo_guardado import RecuerdoGuardado
from asistente.tests.fakes.mundo import ANA, HOGAR, contexto, reloj
from asistente.tests.fakes.recuerdo_repositorio_fake import RecuerdoRepositorioFake


def test_guarda_y_lo_dice_a_la_interfaz():
    recuerdos = RecuerdoRepositorioFake()
    tool = RecordarTool(recuerdos=recuerdos, reloj=reloj())
    r = tool.ejecutar(contexto(), tool.validar('{"texto": "  No contar el  alquiler. "}'))
    assert r.artefacto == RecuerdoGuardado(1, "No contar el alquiler.")
    assert r.para_el_modelo["recordado"] == "No contar el alquiler."
    assert [x.texto for x in recuerdos.listar(ANA, HOGAR)] == ["No contar el alquiler."]


def test_lleno_le_dice_al_modelo_que_hacer():
    recuerdos = RecuerdoRepositorioFake()
    tool = RecordarTool(recuerdos=recuerdos, reloj=reloj())
    for n in range(MAX_RECUERDOS):
        tool.ejecutar(contexto(), tool.validar(f'{{"texto": "Cosa {n}"}}'))
    with pytest.raises(ToolException, match="borre alguno"):
        tool.ejecutar(contexto(), tool.validar('{"texto": "Una más"}'))


def test_largo_no_cabe():
    tool = RecordarTool(recuerdos=RecuerdoRepositorioFake(), reloj=reloj())
    with pytest.raises(ToolException, match="texto"):
        tool.validar('{"texto": "' + "x" * 201 + '"}')
