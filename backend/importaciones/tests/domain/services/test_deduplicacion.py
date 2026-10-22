"""Qué se hace con cada fila del extracto (módulos 75 y 88): lógica pura, sin base de datos."""

from datetime import date, timedelta
from decimal import Decimal

from importaciones.domain.bo.fila import Fila
from importaciones.domain.enums.accion import Accion
from importaciones.domain.services.deduplicacion import clasificar, huellas, repartir
from importaciones.domain.vo.candidato import Candidato
from importaciones.domain.vo.fila_leida import FilaLeida

TRES_DIAS = timedelta(days=3)


def leida(numero, dia, importe, concepto="X", saldo=None):
    return FilaLeida(numero, date(2026, 10, dia), concepto, Decimal(importe), Decimal(saldo) if saldo else None)


def test_huellas_estables_y_distintas_para_movimientos_repetidos():
    cafe = FilaLeida(numero=1, fecha=date(2026, 10, 5), concepto="CAFETERÍA LA PLAZA", importe=Decimal("-1.50"))
    otro_cafe = FilaLeida(numero=2, fecha=date(2026, 10, 5), concepto="Cafeteria la Plaza", importe=Decimal("-1.5"))
    primera, segunda = huellas(1, [cafe, otro_cafe])
    assert primera != segunda  # el mismo café dos veces el mismo día: ocurrencias 1 y 2
    assert huellas(1, [cafe]) == [primera]  # otro extracto que solo trae el primero → misma huella
    assert huellas(2, [cafe]) != [primera]  # otra cuenta, otro movimiento


def test_clasificar_duplicadas_conciliar_y_crear():
    filas = [leida(1, 1, "-45.30"), leida(2, 2, "-45.30"), leida(3, 3, "-9.99"), leida(4, 9, "-61.22")]
    hs = ["h1", "h2", "h3", "h4"]
    candidatos = [
        Candidato(100, date(2026, 10, 2), Decimal("-45.30")),  # el súper apuntado a mano el día 2
        Candidato(200, date(2026, 10, 20), Decimal("-61.22")),  # misma cantidad, pero 11 días después: no
    ]

    resultado = clasificar(filas, hs, existentes={"h3"}, candidatos=candidatos, margen=TRES_DIAS)

    assert [(f.accion, f.coincide_con_id) for f in resultado] == [
        (Accion.CONCILIAR, 100),  # el gasto manual del día 2 "absorbe" la fila del día 1
        (Accion.CREAR, None),  # el mismo importe al día siguiente: ese candidato ya está emparejado
        (Accion.DUPLICADA, None),  # ya importada en otro extracto
        (Accion.CREAR, None),
    ]


def test_repartir_un_lote():
    def fila(huella, accion, coincide=None):
        return Fila(1, date(2026, 10, 1), "X", Decimal("-1"), huella, accion, coincide)

    lote = [
        fila("a", Accion.CREAR),
        fila("b", Accion.CONCILIAR, 7),
        fila("c", Accion.CONCILIAR),
        fila("d", Accion.CREAR),
    ]
    duplicadas, conciliar, crear = repartir(lote, ya_importadas={"d"})  # "d" la creó entretanto otro extracto
    assert [f.huella for f in duplicadas] == ["d"] and [f.huella for f in conciliar] == ["b"]
    assert [(f.huella, f.accion) for f in crear] == [("a", Accion.CREAR), ("c", Accion.CREAR)]  # su gasto ya no existe
