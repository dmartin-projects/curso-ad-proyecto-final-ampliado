"""Módulo 101: lo que puede y lo que no puede hacer el SQL del modelo. Cada test es un ataque o un error que pasa de
verdad (y la barrera que lo para), contra PostgreSQL: lo que importa aquí no se puede probar con fakes.

Con el árbol (sqlglot, ejercicio 1) apagado: casi todos estos ataques ya los pararía él, y aquí se prueba que, si se le
escapara alguno, PostgreSQL lo para igual.

Con transaction=True: la consulta va por OTRA conexión (la del rol), que no vería nada de lo que el test escribiera
dentro de su transacción."""

from datetime import date
from decimal import Decimal

import pytest

from asistente.domain.exceptions.consulta_sql_exception import ConsultaSQLException
from asistente.infrastructure.sql.consultas_sql_postgres import ConsultasSQLPostgres
from conftest import CategoriaFactory, CuentaFactory, HogarFactory, MovimientoFactory

pytestmark = [
    pytest.mark.django_db(transaction=True),
    pytest.mark.usefixtures("rol_sql"),
]


@pytest.fixture
def dos_hogares():
    nuestro, otro = HogarFactory(nombre="Nuestro"), HogarFactory(nombre="Otro")
    cuentas = {h: CuentaFactory(hogar=h, nombre="Común") for h in (nuestro, otro)}
    for hogar, importe in ((nuestro, "-12.50"), (nuestro, "-30.00"), (otro, "-999.00")):
        cuenta = cuentas[hogar]
        MovimientoFactory(
            hogar=hogar, cuenta=cuenta, categoria=CategoriaFactory(hogar=hogar), importe=Decimal(importe),
            fecha=date(2026, 10, 1), notas="nota privada",
        )  # fmt: skip
    return nuestro, otro


def consultar(hogar, sql):
    return ConsultasSQLPostgres(arbol=False).ejecutar(hogar.pk, sql)


def test_solo_ve_su_hogar(dos_hogares):
    nuestro, _ = dos_hogares
    r = consultar(nuestro, "select count(*) as n, sum(importe) as total from movimientos")
    assert (r.columnas, r.filas) == (("n", "total"), ((2, Decimal("-42.50")),))


def test_ni_preguntando_por_otro_hogar_a_la_tabla_de_verdad(dos_hogares):
    nuestro, otro = dos_hogares
    r = consultar(nuestro, f"select count(*) from public.finanzas_movimiento where hogar_id = {otro.pk}")
    assert r.filas == ((0,),)  # la RLS filtra también la tabla, no solo la vista


def test_no_puede_cambiarse_de_hogar(dos_hogares):
    """El hogar no está en una variable que la consulta pueda cambiar: está en una tabla que el rol no puede escribir."""
    nuestro, otro = dos_hogares
    r = consultar(nuestro, f"select set_config('gastos.hogar_id', '{otro.pk}', true), count(*) from movimientos")
    assert r.filas[0][1] == 2
    with pytest.raises(ConsultaSQLException, match="Sin permiso"):
        consultar(nuestro, "select * from asistente_sql.contexto")  # ni siquiera puede leerla


def test_no_puede_volver_a_ser_la_aplicacion(dos_hogares):
    nuestro, _ = dos_hogares
    with pytest.raises(ConsultaSQLException, match="(?i)permission|permiso"):
        consultar(nuestro, "select set_config('role', 'gastos', true)")


def test_ni_columnas_privadas_ni_escribir(dos_hogares):
    nuestro, _ = dos_hogares
    with pytest.raises(ConsultaSQLException, match="Sin permiso"):
        consultar(nuestro, "select notas from public.finanzas_movimiento")
    with pytest.raises(ConsultaSQLException):
        consultar(nuestro, "with x as (delete from public.finanzas_movimiento returning 1) select * from x")


def test_lenta_se_corta(dos_hogares):
    nuestro, _ = dos_hogares
    with pytest.raises(ConsultaSQLException, match="tarda más de 2 s"):
        consultar(nuestro, "select pg_sleep(3)")


def test_las_filas_tienen_tope(dos_hogares, settings):
    nuestro, _ = dos_hogares
    settings.ASISTENTE_SQL_FILAS = 5
    r = consultar(nuestro, "select generate_series(1, 100) as n")
    assert (len(r.filas), r.recortado) == (5, True)


def test_sin_contexto_no_ve_nada(dos_hogares):
    """Si el contexto no se escribiera (un fallo nuestro), el rol no vería nada: falla cerrado."""
    import psycopg

    from asistente.infrastructure.sql.consultas_sql_postgres import _datos_de_conexion

    with psycopg.connect(**_datos_de_conexion()) as conexion:
        assert conexion.execute("select count(*) from movimientos").fetchone() == (0,)
