"""Módulo 101: la comparación, sin modelo (LLMFake) pero con PostgreSQL y el rol de verdad: el SQL que "escribe" el
modelo se ejecuta con la Row Level Security, sobre la casa de los tests."""

import json

import pytest

from asistente.application.agent.agente import Agente
from asistente.application.tools.consultar_sql_tool import ConsultarSQLTool
from asistente.infrastructure import container
from asistente.infrastructure.sql.consultas_sql_postgres import ConsultasSQLPostgres
from asistente.management.commands.comparar_sql_y_tools import comparar
from asistente.tests.fakes.llm_fake import LLMFake

pytestmark = [pytest.mark.usefixtures("rol_sql"), pytest.mark.django_db(transaction=True)]
SEPTIEMBRE = (
    "select sum(importe) as total from movimientos where fecha >= '2026-09-01' and fecha < '2026-10-01' and importe < 0"
)


def test_el_sql_del_modelo_contra_la_casa(casa):
    ana, hogar = casa
    sql = LLMFake([LLMFake.llamar("consultar_sql", sql=SEPTIEMBRE), LLMFake.responder("En septiembre, 776,59 €.")])
    tools = LLMFake([LLMFake.responder("No lo sé.")])
    agentes = {
        "tools": Agente(llm=tools, tools=[]),
        "sql": Agente(llm=sql, tools=[ConsultarSQLTool(consultas=ConsultasSQLPostgres())]),
    }
    salida = comparar(
        [{"pregunta": "¿Septiembre?", "correcta": "776,59"}], container.contexto(ana.pk, hogar.pk), agentes
    )
    resultado = json.loads(sql.peticiones[1].mensajes[-1].resultados[0].contenido)
    assert resultado == {"columnas": ["total"], "filas": [["-776.59"]], "total_filas": 1}  # el mismo dato que las tools
    assert "tools  ✗ 1 vueltas" in salida and "sql    ✓ 2 vueltas" in salida
    assert salida.endswith(
        "tools  0 de 1 correctas · 120 tokens · 1 vueltas\nsql    1 de 1 correctas · 230 tokens · 2 vueltas\n"
    )
