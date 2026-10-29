"""Módulo 93: cuánto cuesta una llamada (Uso y Precio). Decimal, nunca float: son dólares y se suman."""

from decimal import Decimal

from asistente.domain.vo.precio import Precio
from asistente.domain.vo.uso import Uso

GPT_OSS_120B = Precio(Decimal("0.15"), Decimal("0.60"), Decimal("0.075"))


def test_los_usos_se_suman():
    total = Uso(100, 20, 5, 0) + Uso(300, 40, 10, 128)
    assert total == Uso(400, 60, 15, 128)
    assert total.total == 460


def test_coste_de_una_llamada():
    # 92 de entrada a 0,15 $ y 76 de salida (razonamiento incluido) a 0,60 $ por millón
    assert GPT_OSS_120B.coste(Uso(entrada=92, salida=76, razonamiento=44)) == Decimal("0.000059")


def test_la_entrada_desde_la_cache_es_mas_barata():
    sin_cache = GPT_OSS_120B.coste(Uso(entrada=2000, salida=100))
    con_cache = GPT_OSS_120B.coste(Uso(entrada=2000, salida=100, cache=1536))
    assert (sin_cache, con_cache) == (Decimal("0.000360"), Decimal("0.000245"))
