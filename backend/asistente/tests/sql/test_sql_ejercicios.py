"""Ejercicios del módulo 101: el SQL leído como árbol (sqlglot), el coste estimado antes de ejecutar y la auditoría."""

import logging
from datetime import date
from decimal import Decimal

import pytest

from asistente.domain.exceptions.consulta_sql_exception import ConsultaSQLException
from asistente.infrastructure.sql.consultas_sql_postgres import ConsultasSQLPostgres
from asistente.infrastructure.sql.validador_sqlglot import validar_arbol
from conftest import CategoriaFactory, CuentaFactory, HogarFactory, MovimientoFactory

METRICA = "gastos.asistente.consultas_sql"


# ── Ejercicio 1: el árbol ──
@pytest.mark.parametrize(
    "sql, error",
    [
        ("select * from public.finanzas_movimiento", "Solo las vistas"),
        ("select * from movimientos m join usuarios_usuario u on true", "usuarios_usuario"),
        ("select * from asistente_sql.contexto", "contexto"),
        ("select pg_sleep(3)", "pg_sleep"),
        ("select set_config('role', 'gastos', true)", "set_config"),
        ("select pg_read_file('/etc/passwd')", "pg_read_file"),
        ("select * from dblink('host=otra', 'select 1') as t(x int)", "(?i)dblink"),
        ("with b as (delete from movimientos returning *) select * from b", "DELETE"),
        ("select * into copia from movimientos", "INTO"),
        ("select 1; select 2", "Una sola"),
        ("selec concepto from movimientos", "No se entiende|Solo consultas"),
    ],
)
def test_lo_que_el_arbol_no_deja(sql, error):
    with pytest.raises(ConsultaSQLException, match=error):
        validar_arbol(sql)


@pytest.mark.parametrize(
    "sql",
    [
        "select c.nombre, sum(m.importe) as total from movimientos m join categorias c on c.id = m.categoria_id "
        "group by 1 order by 2",
        "with mes as (select date_trunc('month', fecha) as mes, sum(importe) as t from movimientos group by 1) "
        "select to_char(mes, 'YYYY-MM'), t from mes",
        "select extract(year from fecha), count(*), coalesce(sum(importe), 0) from asistente_sql.movimientos group by 1",
        "select nombre from cuentas union all select nombre from categorias",
    ],
)
def test_lo_que_el_arbol_deja(sql):
    validar_arbol(sql)  # sin excepción


# ── Ejercicios 2 y 3, contra PostgreSQL ──
@pytest.fixture
def nuestro():
    hogar = HogarFactory(nombre="Nuestro")
    cuenta = CuentaFactory(hogar=hogar)
    for d in range(1, 4):
        MovimientoFactory(
            hogar=hogar, cuenta=cuenta, categoria=CategoriaFactory(hogar=hogar), importe=Decimal("-10"),
            fecha=date(2026, 10, d),
        )  # fmt: skip
    return hogar


def cuenta(telemetria, resultado):
    return telemetria.metrica(METRICA).get((("resultado", resultado),), 0)


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("rol_sql")
def test_una_consulta_demasiado_cara_ni_se_ejecuta(nuestro, settings, telemetria):
    """Un producto cartesiano de 1000 × 1000 × 1000 filas: el planificador lo calcula y se rechaza sin leer nada."""
    antes = cuenta(telemetria, "rechazada")
    sql = "select count(*) from generate_series(1, 1000) a, generate_series(1, 1000) b, generate_series(1, 1000) c"
    with pytest.raises(ConsultaSQLException, match="demasiado cara"):
        ConsultasSQLPostgres(arbol=False).ejecutar(nuestro.pk, sql)
    assert cuenta(telemetria, "rechazada") == antes + 1

    settings.ASISTENTE_SQL_COSTE_MAXIMO = 10**12  # con el límite muy alto, la misma la corta el statement_timeout
    with pytest.raises(ConsultaSQLException, match="tarda más"):
        ConsultasSQLPostgres(arbol=False).ejecutar(nuestro.pk, sql)
    assert cuenta(telemetria, "timeout") >= 1


@pytest.mark.django_db(transaction=True)
@pytest.mark.usefixtures("rol_sql")
def test_cada_consulta_deja_una_linea_y_una_medida(nuestro, telemetria, caplog):
    antes = {r: cuenta(telemetria, r) for r in ("ok", "rechazada")}
    caplog.set_level(logging.INFO, logger="asistente.infrastructure.sql.consultas_sql_postgres")
    r = ConsultasSQLPostgres().ejecutar(nuestro.pk, "select count(*) from movimientos")
    assert r.filas == ((3,),)
    with pytest.raises(ConsultaSQLException):
        ConsultasSQLPostgres().ejecutar(nuestro.pk, "select pg_sleep(1)")

    ok, rechazada = (rec.asistente_sql for rec in caplog.records)
    assert ok["resultado"] == "ok" and ok["hogar_id"] == nuestro.pk and ok["filas"] == 1 and ok["coste"] > 0
    assert rechazada["resultado"] == "rechazada" and "pg_sleep" in rechazada["error"]
    assert "select" not in str(ok).lower()  # el SQL no va al log: su huella (puede llevar lo que el usuario escribió)
    assert len(ok["sql"]) == 12
    assert {r: cuenta(telemetria, r) - antes[r] for r in antes} == {"ok": 1, "rechazada": 1}
