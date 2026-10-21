"""La API: autenticación con el JWT de Django, permisos por hogar y los cálculos (módulo 85)."""

import json
from datetime import date

import pytest
from fastapi.testclient import TestClient

from estadisticas.api import app
from estadisticas.bd import sesion
from estadisticas.proyeccion import aplicar

cliente = TestClient(app)
URL = "/estadisticas/v1/hogares/1"
version = iter(range(1, 10_000))


def evento(topic, clave, datos):
    with sesion() as s, s.begin():
        aplicar(s, topic, clave, json.dumps(datos).encode(), {"version": str(next(version)), "esquema": "1"})


def miembro(usuario_id=5, hogar_id=1):
    evento(
        "gastos.membresias",
        f"{hogar_id}:{usuario_id}",
        {"hogar_id": hogar_id, "usuario_id": usuario_id, "rol": "lector"},
    )


def movimiento(pk, fecha, importe, hogar_id=1, revisado=True):
    evento("gastos.movimientos", str(pk), {"id": pk, "hogar_id": hogar_id, "cuenta_id": 1, "fecha": fecha,
                                           "importe": importe, "categoria_id": None, "comercio_id": None,
                                           "origen": "manual", "revisado": revisado})  # fmt: skip


def get(url, tk=None, **params):
    return cliente.get(url, params=params, headers={"Authorization": f"Bearer {tk}"} if tk else {})


# ── Autenticación y permisos ──
@pytest.mark.parametrize(
    "caso",
    ["sin_token", "firma_mala", "caducado", "refresh", "basura"],
)
def test_401(token, caso):
    miembro()
    tk = {
        "sin_token": None,
        "firma_mala": token(5, clave="otra-clave-distinta-de-al-menos-32-bytes"),
        "caducado": token(5, caduca_en=-10),
        "refresh": token(5, tipo="refresh"),
        "basura": "esto.no.es-un-jwt",
    }[caso]
    assert get(f"{URL}/tendencia", tk).status_code == 401


def test_alg_none_rechazado(token):
    """El ataque clásico: un token sin firma que dice "alg": "none". algorithms=["HS256"] lo para."""
    import jwt

    miembro()
    falso = jwt.encode({"token_type": "access", "exp": 9999999999, "user_id": "5"}, None, algorithm="none")
    assert get(f"{URL}/tendencia", falso).status_code == 401


def test_no_miembro_es_404(token):
    miembro(usuario_id=5)
    assert get(f"{URL}/tendencia", token(6)).status_code == 404  # 404: ni siquiera se sabe si el hogar existe
    assert get(f"{URL}/tendencia", token(5)).status_code == 200


# ── Cálculos ──
def test_tendencia_con_meses_vacios(token):
    miembro()
    movimiento(1, "2026-08-03", "-30.00")
    movimiento(2, "2026-08-20", "-20.50")
    movimiento(3, "2026-10-01", "2000.00")
    movimiento(4, "2026-10-02", "-100.00")
    movimiento(5, "2026-10-02", "-999.00", hogar_id=2)  # de otro hogar: no cuenta
    r = get(f"{URL}/tendencia", token(5), meses=3, hasta="2026-10")
    assert r.status_code == 200
    assert r.json()["meses"] == [
        {"mes": "2026-08", "gastos": "50.50", "ingresos": "0", "ahorro": "-50.50"},
        {"mes": "2026-09", "gastos": "0", "ingresos": "0", "ahorro": "0"},  # sin movimientos, pero está
        {"mes": "2026-10", "gastos": "100.00", "ingresos": "2000.00", "ahorro": "1900.00"},
    ]


def test_dias_semana(token):
    miembro()
    # Septiembre de 2026: empieza en martes y tiene 30 días → 5 martes y 5 miércoles, 4 de los demás
    assert date(2026, 9, 1).isoweekday() == 2
    movimiento(1, "2026-09-01", "-50.00")  # martes
    movimiento(2, "2026-09-08", "-50.00")  # martes
    movimiento(3, "2026-09-07", "-40.00")  # lunes
    movimiento(4, "2026-09-09", "100.00")  # miércoles, ingreso: no es gasto
    movimiento(5, "2026-08-31", "-999.00")  # agosto: fuera del periodo
    r = get(f"{URL}/dias-semana", token(5), meses=1, hasta="2026-09").json()
    assert (r["desde"], r["hasta"]) == ("2026-09-01", "2026-09-30")
    medias = {d["nombre"]: d["gasto_medio"] for d in r["dias"]}
    assert medias["martes"] == "20.00"  # 100 € entre 5 martes
    assert medias["lunes"] == "10.00"  # 40 € entre 4 lunes
    assert medias["miércoles"] == "0.00"


def test_el_mes_en_curso_solo_cuenta_hasta_hoy(token):
    miembro()
    hoy = date.today()
    r = get(f"{URL}/dias-semana", token(5), meses=1).json()
    assert r["desde"] == f"{hoy:%Y-%m}-01" and r["hasta"] == hoy.isoformat()


def test_un_mes_futuro_cuenta_como_el_actual(token):
    miembro()
    hoy = date.today()
    r = get(f"{URL}/dias-semana", token(5), meses=1, hasta=f"{hoy.year + 1}-{hoy.month:02d}")
    assert r.status_code == 200
    assert (r.json()["desde"], r.json()["hasta"]) == (f"{hoy:%Y-%m}-01", hoy.isoformat())
    assert all(d["gasto_medio"] == "0.00" for d in r.json()["dias"])  # sin gastos: 0, nunca "-0.00"


def test_hasta_mal_formado(token):
    miembro()
    assert get(f"{URL}/tendencia", token(5), hasta="octubre").status_code == 422


def test_salud():
    assert get("/estadisticas/v1/salud").json() == {"bd": "ok", "ultimo_evento": None}


# ── Ejercicio 4 ──
def test_sin_revisar(token):
    miembro()
    movimiento(1, "2026-09-03", "-30.00", revisado=False)
    movimiento(2, "2026-09-04", "-20.00", revisado=False)
    movimiento(3, "2026-09-05", "-99.00")  # revisado: no cuenta
    movimiento(4, "2026-10-01", "1500.00", revisado=False)  # ingreso sin revisar: cuenta, pero no suma gasto
    r = get(f"{URL}/sin-revisar", token(5), meses=2, hasta="2026-10").json()
    assert r["meses"] == [
        {"mes": "2026-09", "movimientos": 2, "gastos": "50.00"},
        {"mes": "2026-10", "movimientos": 1, "gastos": "0"},
    ]
