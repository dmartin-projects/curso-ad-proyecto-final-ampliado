"""Aplicar eventos: idempotente y a prueba de desorden (módulo 85)."""

import json
from decimal import Decimal

import pytest
from sqlalchemy import select

from estadisticas.bd import Membresia, Movimiento, sesion
from estadisticas.proyeccion import EsquemaDesconocido, aplicar

MOV, MEMB = "gastos.movimientos", "gastos.membresias"


def mov(pk=7, importe="-10.00", **extra) -> bytes:
    datos = {"id": pk, "hogar_id": 1, "cuenta_id": 1, "fecha": "2026-10-01", "importe": importe,
             "categoria_id": 3, "comercio_id": None, "origen": "manual", "revisado": True} | extra  # fmt: skip
    return json.dumps(datos).encode()


def cab(version, esquema="1", tipo="movimiento.actualizado"):
    return {"version": str(version), "esquema": esquema, "tipo": tipo}


def aplicar_uno(*args):
    with sesion() as s, s.begin():
        return aplicar(s, *args)


def importe(pk=7):
    with sesion() as s:
        return s.scalar(select(Movimiento.importe).where(Movimiento.id == pk))


def test_crea_y_actualiza():
    assert aplicar_uno(MOV, "7", mov(importe="-10.00"), cab(1)) == "guardado"
    assert aplicar_uno(MOV, "7", mov(importe="-12.50"), cab(2)) == "guardado"
    assert importe() == Decimal("-12.50")


def test_un_duplicado_no_cambia_nada():
    aplicar_uno(MOV, "7", mov(importe="-10.00"), cab(5))
    assert aplicar_uno(MOV, "7", mov(importe="-10.00"), cab(5)) == "ignorado"  # al menos una vez → a veces dos


def test_una_version_vieja_no_pisa_una_nueva():
    aplicar_uno(MOV, "7", mov(importe="-20.00"), cab(9))
    assert aplicar_uno(MOV, "7", mov(importe="-10.00"), cab(4)) == "ignorado"
    assert importe() == Decimal("-20.00")


def test_tombstone_borra_y_uno_viejo_no_resucita_si_llega_despues_de_otra_version():
    aplicar_uno(MOV, "7", mov(), cab(1))
    assert aplicar_uno(MOV, "7", None, cab(2, tipo="movimiento.eliminado")) == "borrado"
    assert importe() is None
    assert aplicar_uno(MOV, "7", None, cab(2)) == "ignorado"  # el tombstone repetido no hace nada


def test_tombstone_viejo_no_borra_una_version_nueva():
    aplicar_uno(MOV, "7", mov(), cab(10))
    assert aplicar_uno(MOV, "7", None, cab(3)) == "ignorado"
    assert importe() is not None


def test_campos_nuevos_se_ignoran():
    """Lector tolerante: Django puede añadir campos al mensaje sin romper a quien no los usa."""
    assert aplicar_uno(MOV, "7", mov(etiquetas=["viaje"], moneda="EUR"), cab(1)) == "guardado"


def test_esquema_desconocido_para():
    with pytest.raises(EsquemaDesconocido):
        aplicar_uno(MOV, "7", mov(), cab(1, esquema="2"))


def test_membresias():
    assert (
        aplicar_uno(MEMB, "1:5", json.dumps({"hogar_id": 1, "usuario_id": 5, "rol": "lector"}).encode(), cab(1))
        == "guardado"
    )
    assert (
        aplicar_uno(MEMB, "1:5", json.dumps({"hogar_id": 1, "usuario_id": 5, "rol": "admin"}).encode(), cab(2))
        == "guardado"
    )
    with sesion() as s:
        assert s.scalar(select(Membresia.rol)) == "admin"
    assert aplicar_uno(MEMB, "1:5", None, cab(3)) == "borrado"


def test_un_mensaje_antiguo_sin_revisado_vale_true():
    """Ejercicio 4: mensajes de antes de que el servicio leyera "revisado" (los de un relay viejo)."""
    datos = json.loads(mov())
    datos.pop("revisado")
    assert aplicar_uno(MOV, "7", json.dumps(datos).encode(), cab(1)) == "guardado"
    with sesion() as s:
        assert s.scalar(select(Movimiento.revisado)) is True
