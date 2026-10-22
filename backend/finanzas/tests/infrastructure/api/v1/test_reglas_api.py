"""Las reglas del dominio, vistas desde la API (módulo 87): el refactor conserva lo que la API ya hacía.

Cada regla responde con su error del formulario (400 con su campo), nunca con un 500; la jerarquía de
categorías no se rompe; y los efectos de un cambio (el dashboard, la alerta del mes de antes) llegan igual.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.core.cache import cache

from conftest import CategoriaFactory, CuentaFactory, MovimientoFactory, PresupuestoFactory
from core.models import RegistroAuditoria

pytestmark = pytest.mark.django_db


def url(hogar, recurso):
    return f"/api/v1/hogares/{hogar.pk}/{recurso}/"


@pytest.fixture
def admin(hogar_con_roles, cliente):
    hogar, roles = hogar_con_roles
    return hogar, cliente(roles["admin"])


def errores(respuesta) -> dict:
    assert respuesta.status_code == 400, respuesta.content
    return respuesta.json()["errors"]


def test_las_constraints_llegan_como_errores_del_formulario(admin):
    hogar, c = admin
    comida = CategoriaFactory(hogar=hogar, nombre="Comida")
    CuentaFactory(hogar=hogar, nombre="Común")
    PresupuestoFactory(hogar=hogar, categoria=comida, mes=date(2026, 10, 1), importe=10)

    pres = url(hogar, "presupuestos")
    assert "importe" in errores(c.post(pres, {"categoria": comida.pk, "mes": "2026-11-01", "importe": "0"}))
    assert "categoria" in errores(c.post(pres, {"categoria": comida.pk, "mes": "2026-10-15", "importe": "20"}))
    assert "nombre" in errores(c.post(url(hogar, "cuentas"), {"nombre": "Común"}))
    assert "nombre" in errores(c.post(url(hogar, "categorias"), {"nombre": "Comida"}))
    assert errores(c.post(url(hogar, "categorias"), {"nombre": "X", "color": "rojo"})) == {
        "color": ["El color debe tener el formato #rrggbb."]
    }


def test_la_jerarquia_de_categorias_no_se_rompe(admin):
    hogar, c = admin
    comida = CategoriaFactory(hogar=hogar, nombre="Comida")
    ocio = CategoriaFactory(hogar=hogar, nombre="Ocio")
    CategoriaFactory(hogar=hogar, nombre="Cine", padre=ocio)
    cats = url(hogar, "categorias")

    assert "padre" in errores(c.patch(f"{cats}{comida.pk}/", {"padre": comida.pk}))  # madre de sí misma
    assert "padre" in errores(c.patch(f"{cats}{ocio.pk}/", {"padre": comida.pk}))  # Comida › Ocio › Cine
    fruta = c.post(cats, {"nombre": "Fruta", "padre": comida.pk}).json()
    assert errores(c.post(cats, {"nombre": "Manzanas", "padre": fruta["id"]})) == {
        "padre": ["Solo se permiten dos niveles de categorías."]  # el mensaje de siempre
    }


def test_crear_un_presupuesto_devuelve_lo_gastado(admin):
    hogar, c = admin
    comida = CategoriaFactory(hogar=hogar)
    MovimientoFactory(cuenta=CuentaFactory(hogar=hogar), categoria=comida, fecha=date(2026, 10, 3), importe=-25)
    r = c.post(url(hogar, "presupuestos"), {"categoria": comida.pk, "mes": "2026-10-20", "importe": "100"})
    assert r.status_code == 201
    assert (r.json()["mes"], r.json()["gastado"], r.json()["porcentaje"]) == ("2026-10-01", "-25.00", 25)


def test_borrar_un_presupuesto_invalida_el_dashboard(admin, django_capture_on_commit_callbacks):
    hogar, c = admin
    comida = CategoriaFactory(hogar=hogar)
    p = PresupuestoFactory(hogar=hogar, categoria=comida, mes=date(2026, 10, 1), importe=10)
    dashboard = url(hogar, "dashboard")
    assert len(c.get(dashboard, {"mes": "2026-10"}).json()["presupuestos"]) == 1
    with django_capture_on_commit_callbacks(execute=True):
        assert c.delete(f"{url(hogar, 'presupuestos')}{p.pk}/").status_code == 204
    assert c.get(dashboard, {"mes": "2026-10"}).json()["presupuestos"] == []


def test_cambiar_la_fecha_de_mes_rearma_la_alerta_del_mes_viejo(admin, django_capture_on_commit_callbacks):
    hogar, c = admin
    comida = CategoriaFactory(hogar=hogar)
    p = PresupuestoFactory(hogar=hogar, categoria=comida, mes=date(2026, 10, 1), importe=100, alerta_enviada=True)
    gasto = MovimientoFactory(
        cuenta=CuentaFactory(hogar=hogar), categoria=comida, fecha=date(2026, 10, 5), importe=-150
    )
    cache.clear()  # las comprobaciones se agrupan 10 s (core/infrastructure/tasks/agrupar.py)
    with django_capture_on_commit_callbacks(execute=True):
        r = c.patch(f"{url(hogar, 'movimientos')}{gasto.pk}/", {"fecha": "2026-09-28"})  # era de septiembre
    assert r.status_code == 200
    p.refresh_from_db()
    assert p.alerta_enviada is False  # octubre ya no está superado: si se vuelve a superar, se volverá a avisar


def test_la_auditoria_de_una_modificacion_es_la_de_siempre(admin):
    hogar, c = admin
    m = MovimientoFactory(cuenta=CuentaFactory(hogar=hogar), importe=Decimal("-10.00"), concepto="Cena")
    c.patch(f"{url(hogar, 'movimientos')}{m.pk}/", {"importe": "-11", "concepto": "Cena de cumpleaños"})
    registro = RegistroAuditoria.objects.get(accion="modificar")
    assert registro.cambios == {"importe": ["-10.00", "-11.00"], "concepto": ["Cena", "Cena de cumpleaños"]}
    assert registro.representacion == f"{m.fecha} Cena de cumpleaños -11.00" and registro.objeto == m


def test_la_tarea_conserva_su_nombre():
    from finanzas.infrastructure.tasks.comprobar_presupuestos_task import comprobar_presupuestos_tarea

    # el nombre que tenía en finanzas/tasks.py (módulo 76): los mensajes ya encolados lo siguen encontrando
    assert comprobar_presupuestos_tarea.name == "finanzas.tasks.comprobar_presupuestos_tarea"
