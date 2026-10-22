"""ProcesarLoteUseCase con fakes (módulo 89): idempotencia, venenosos, transacción. Sin PostgreSQL ni Kafka."""

from decimal import Decimal

import pytest

from estadisticas.domain.enums.resultado import Resultado
from estadisticas.domain.exceptions.esquema_desconocido_exception import EsquemaDesconocidoException
from tests.fakes.mundo import MARCA, MEMB, MOV, Mundo, borrado, lote, membresia, mensaje, movimiento

G, IG, B, A = Resultado.GUARDADO, Resultado.IGNORADO, Resultado.BORRADO, Resultado.APARCADO


def importes(mundo: Mundo) -> dict[int, Decimal]:
    return {pk: m.importe for pk, m in mundo.memoria.movimientos.items()}


def test_aplica_el_lote_en_una_transaccion_y_anota_el_progreso():
    mundo = Mundo()
    mensajes = [
        movimiento(1, offset=10),
        movimiento(2, offset=11, particion=1),
        membresia(1, 5, offset=12, particion=1),
    ]
    assert mundo.procesar_lote().ejecutar(lote(mensajes)) == 3
    assert importes(mundo) == {1: Decimal("-10.00"), 2: Decimal("-10.00")}
    assert mundo.memoria.membresias[(1, 5)].rol == "lector"
    assert mundo.memoria.progreso == {(MOV, 0): (10, MARCA), (MOV, 1): (11, MARCA), (MEMB, 1): (12, MARCA)}
    assert (mundo.uow.confirmadas, mundo.uow.deshechas) == (1, 0)


def test_idempotente_por_version():
    """Al menos una vez → a veces dos; y una versión vieja que llega tarde no pisa una nueva."""
    mundo = Mundo()
    caso = mundo.procesar_lote()
    caso.ejecutar(lote([movimiento(7, "-20.00", version=9, offset=0), movimiento(7, "-20.00", version=9, offset=1)]))
    caso.ejecutar(lote([movimiento(7, "-10.00", version=4, offset=2), borrado(7, version=3, offset=3)]))
    assert importes(mundo) == {7: Decimal("-20.00")}
    assert mundo.trazas.resultados == {0: G, 1: IG, 2: IG, 3: IG}
    caso.ejecutar(lote([borrado(7, version=10, offset=4), borrado(7, version=10, offset=5)]))  # el tombstone, repetido
    assert importes(mundo) == {} and (mundo.trazas.resultados[4], mundo.trazas.resultados[5]) == (B, IG)


def test_un_venenoso_se_aparca_y_los_demas_se_aplican():
    mundo = Mundo()
    mensajes = [
        movimiento(1, offset=0),
        mensaje(MOV, "2", b"{esto no es JSON", 1, offset=1),
        movimiento(3, importe="abc", offset=2),
        movimiento(4, importe="99999999999.00", offset=3),  # no cabe en Numeric(12, 2): lo dice el repositorio
        movimiento(5, offset=4),
    ]
    assert mundo.procesar_lote().ejecutar(lote(mensajes)) == 5
    assert set(importes(mundo)) == {1, 5}
    assert [(m.offset, type(e).__name__) for m, e in mundo.aparcados.guardados] == [
        (1, "JSONDecodeError"),
        (2, "InvalidOperation"),
        (3, "ValueError"),
    ]
    assert mundo.trazas.resultados == {0: G, 1: A, 2: A, 3: A, 4: G}
    assert mundo.memoria.progreso[(MOV, 0)][0] == 4  # los aparcados también cuentan como procesados
    assert (mundo.uow.confirmadas, mundo.uow.deshechas) == (1, 1)  # el primer intento (sin cuidado) se deshizo


def test_sin_aparcados_a_salvo_no_se_confirma_nada():
    mundo = Mundo(dlq_caida=True)
    with pytest.raises(RuntimeError):
        mundo.procesar_lote().ejecutar(lote([movimiento(1), mensaje(MOV, "2", b"roto", 1, offset=1)]))
    assert importes(mundo) == {} and mundo.memoria.progreso == {}  # el lote se repetirá entero


def test_un_esquema_desconocido_para_sin_confirmar_nada():
    mundo = Mundo()
    with pytest.raises(EsquemaDesconocidoException):
        mundo.procesar_lote().ejecutar(lote([movimiento(1), movimiento(2, offset=1, esquema="2")]))
    assert importes(mundo) == {} and mundo.aparcados.guardados == []


def test_un_topic_ajeno_se_ignora():
    mundo = Mundo()
    mundo.procesar_lote().ejecutar(lote([mensaje("otro.topic", "1", b"{}", 1)]))
    assert mundo.trazas.resultados == {0: IG} and mundo.memoria.progreso == {("otro.topic", 0): (0, MARCA)}


def test_membresias():
    mundo = Mundo()
    caso = mundo.procesar_lote()
    caso.ejecutar(lote([membresia(1, 5, "lector", version=1), membresia(1, 5, "admin", version=2, offset=1)]))
    assert mundo.memoria.membresias[(1, 5)].rol == "admin"
    caso.ejecutar(lote([mensaje(MEMB, "1:5", None, 3, offset=2)]))
    assert mundo.memoria.membresias == {}


# ── Ejercicio 1: reintentar los aparcados ──
def test_un_reintento_no_hace_retroceder_el_progreso():
    mundo = Mundo()
    caso = mundo.procesar_lote()
    caso.ejecutar(lote([movimiento(1, offset=50)]))
    caso.ejecutar(lote([movimiento(2, offset=7)], anotar_progreso=False))  # un aparcado de hace tiempo, reintentado
    assert set(importes(mundo)) == {1, 2} and mundo.memoria.progreso == {(MOV, 0): (50, MARCA)}
