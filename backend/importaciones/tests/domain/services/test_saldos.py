"""Los saldos de un extracto deben cuadrar (módulos 75 y 88), sin base de datos."""

from datetime import date
from decimal import Decimal

from importaciones.domain.services.saldos import comprobar_saldos
from importaciones.domain.vo.fila_leida import FilaLeida
from importaciones.domain.vo.lectura import Lectura


def leida(numero, dia, importe, concepto="X", saldo=None):
    return FilaLeida(numero, date(2026, 10, dia), concepto, Decimal(importe), Decimal(saldo) if saldo else None)


def test_el_saldo_delata_una_fila_que_falta_en_cualquier_orden():
    lectura = Lectura([leida(1, 1, "-10", saldo="990"), leida(2, 3, "-10", saldo="970")])
    comprobar_saldos(lectura)
    assert lectura.avisos == [
        {"linea": 2, "mensaje": "El saldo no cuadra con la fila anterior: revisa que no falte ninguna."}
    ]
    descendente = Lectura([leida(1, 2, "-10", saldo="980"), leida(2, 1, "-10", saldo="990")])
    comprobar_saldos(descendente)
    assert descendente.avisos == []
