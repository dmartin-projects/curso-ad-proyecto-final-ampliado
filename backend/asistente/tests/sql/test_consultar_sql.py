"""Módulo 101: la tool consultar_sql y lo que se comprueba antes de mandar nada a PostgreSQL."""

from datetime import date
from decimal import Decimal

import pytest

from asistente.application.tools.consultar_sql_tool import ConsultarSQLTool
from asistente.domain.exceptions.consulta_sql_exception import ConsultaSQLException
from asistente.domain.read_models.resultado_sql import ResultadoSQL
from asistente.domain.services.validar_sql import validar_sql
from asistente.domain.vo.consulta_sql import ConsultaSQL
from asistente.tests.fakes.consultas_sql_fake import ConsultasSQLFake
from asistente.tests.fakes.mundo import HOGAR, contexto


@pytest.mark.parametrize(
    "sql, error",
    [
        ("", "vacía"),
        ("delete from movimientos", "SELECT o WITH"),
        ("select 1; select 2", "Una sola"),
        ("select 1 -- y ahora otra cosa", "comentarios"),
        ("select /* */ 1", "comentarios"),
    ],
)
def test_lo_que_no_se_manda(sql, error):
    with pytest.raises(ConsultaSQLException, match=error):
        validar_sql(sql)


def test_lo_que_si():
    assert validar_sql("  SELECT concepto FROM movimientos WHERE concepto = 'a;b' ;") == (
        "SELECT concepto FROM movimientos WHERE concepto = 'a;b'"  # el ; de un texto no separa nada
    )
    assert validar_sql("with x as (select 1) select * from x").startswith("with")


def test_la_tool_da_al_modelo_poco_y_a_la_interfaz_todo():
    filas = tuple((date(2026, 1 + d // 28, 1 + d % 28), Decimal(f"-{d}.50")) for d in range(60))
    consultas = ConsultasSQLFake(ResultadoSQL(("fecha", "importe"), filas, False, 12))
    tool = ConsultarSQLTool(consultas=consultas)
    r = tool.ejecutar(contexto(), tool.validar('{"sql": "select fecha, importe from movimientos"}'))
    assert consultas.ejecutadas == [(HOGAR, "select fecha, importe from movimientos")]  # el hogar, de la sesión
    assert len(r.para_el_modelo["filas"]) == 50 and r.para_el_modelo["total_filas"] == 60 and "nota" in r.para_el_modelo
    assert r.para_el_modelo["filas"][1] == ["2026-01-02", "-1.50"]  # fechas e importes, en JSON
    assert isinstance(r.artefacto, ConsultaSQL) and len(r.artefacto.filas) == 60


def test_un_error_de_postgres_vuelve_al_modelo():
    tool = ConsultarSQLTool(consultas=ConsultasSQLFake(ConsultaSQLException('Error de PostgreSQL: column "total" no')))
    with pytest.raises(ConsultaSQLException, match="total"):
        tool.ejecutar(contexto(), tool.validar('{"sql": "select total from movimientos"}'))
