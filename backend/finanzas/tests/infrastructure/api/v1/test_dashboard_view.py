"""El dashboard por la API (módulos 77 y 87): permisos, formato, mes por defecto, caché, ETag e invalidación."""

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from finanzas.models import Presupuesto

pytestmark = pytest.mark.django_db


def url(hogar):
    return f"/api/v1/hogares/{hogar.pk}/dashboard/"


def test_api_permisos_formato_y_validacion(datos, cliente):
    hogar, roles, _, _ = datos
    r = cliente(roles["lector"]).get(url(hogar), {"mes": "2026-10"})
    assert r.status_code == 200
    assert r.data["mes"] == "2026-10" and r.data["gastos"] == "37.50" and r.data["evolucion"][-1]["mes"] == "2026-10"
    assert cliente(roles["ajeno"]).get(url(hogar)).status_code == 404
    assert cliente(roles["lector"]).get(url(hogar), {"mes": "octubre"}).status_code == 400


@pytest.mark.parametrize("zona, esperado", [("Europe/Madrid", "2026-11"), ("America/New_York", "2026-10")])
def test_el_mes_por_defecto_depende_de_la_zona_del_hogar(datos, cliente, time_machine, zona, esperado):
    hogar, roles, _, _ = datos
    hogar.zona_horaria = zona
    hogar.save()
    time_machine.move_to(datetime(2026, 10, 31, 23, 30, tzinfo=ZoneInfo("UTC")))  # en Madrid ya es 1 de noviembre
    assert cliente(roles["lector"]).get(url(hogar)).data["mes"] == esperado


def test_cache_etag_e_invalidacion(datos, cliente, django_assert_num_queries, django_capture_on_commit_callbacks):
    hogar, roles, _, ocio = datos
    c = cliente(roles["miembro"])

    primera = c.get(url(hogar), {"mes": "2026-10"})
    with django_assert_num_queries(1):  # solo la membresía: el resto sale de la caché
        assert c.get(url(hogar), {"mes": "2026-10"}).data == primera.data
    etag = primera.headers["ETag"]
    assert c.get(url(hogar), {"mes": "2026-10"}, HTTP_IF_NONE_MATCH=etag).status_code == 304

    with django_capture_on_commit_callbacks(execute=True):  # un gasto nuevo → movimientos_cambiados → versión nueva
        c.post(
            f"/api/v1/hogares/{hogar.pk}/movimientos/",
            {"fecha": "2026-10-09", "importe": "-12.50", "concepto": "Cine", "cuenta": ocio.hogar.cuentas.first().pk},
        )

    r = c.get(url(hogar), {"mes": "2026-10"}, HTTP_IF_NONE_MATCH=etag)
    assert r.status_code == 200 and r.headers["ETag"] != etag
    assert r.data["gastos"] == "50.00"


def test_renombrar_una_categoria_invalida(datos, cliente, django_capture_on_commit_callbacks):
    hogar, roles, comida, _ = datos
    c = cliente(roles["admin"])
    c.get(url(hogar), {"mes": "2026-10"})
    with django_capture_on_commit_callbacks(execute=True):
        c.patch(f"/api/v1/hogares/{hogar.pk}/categorias/{comida.pk}/", {"nombre": "Alimentación"})
    nombres = [x["nombre"] for x in c.get(url(hogar), {"mes": "2026-10"}).data["por_categoria"]]
    assert "Alimentación" in nombres


def test_borrar_un_presupuesto_invalida(datos, cliente, django_capture_on_commit_callbacks):
    hogar, roles, comida, _ = datos
    c = cliente(roles["admin"])
    assert len(c.get(url(hogar), {"mes": "2026-10"}).data["presupuestos"]) == 1
    presupuesto = Presupuesto.objects.get(hogar=hogar, categoria=comida)
    with django_capture_on_commit_callbacks(execute=True):
        assert c.delete(f"/api/v1/hogares/{hogar.pk}/presupuestos/{presupuesto.pk}/").status_code == 204
    assert c.get(url(hogar), {"mes": "2026-10"}).data["presupuestos"] == []
