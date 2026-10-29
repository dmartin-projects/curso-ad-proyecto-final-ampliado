"""Módulos 27, 88 y 94: el circuit breaker compartido (estado en la caché)."""

import pytest
from django.core.cache import cache

from core.infrastructure.cache.circuit_breaker import CircuitBreaker
from core.infrastructure.cache.circuito_abierto_exception import CircuitoAbiertoException


@pytest.fixture(autouse=True)
def cache_vacia():
    cache.clear()


def fallar():
    raise ConnectionError("no responde")


def test_se_abre_tras_el_umbral_de_fallos_seguidos():
    breaker = CircuitBreaker("prueba", umbral=2, enfriamiento=60)
    for _ in range(2):
        with pytest.raises(ConnectionError):
            breaker.llamar(fallar)
    assert breaker.abierto
    with pytest.raises(CircuitoAbiertoException):
        breaker.llamar(lambda: "no llega")


def test_un_exito_pone_el_contador_a_cero():
    breaker = CircuitBreaker("prueba", umbral=2, enfriamiento=60)
    with pytest.raises(ConnectionError):
        breaker.llamar(fallar)
    assert breaker.llamar(lambda: "ok") == "ok"
    with pytest.raises(ConnectionError):
        breaker.llamar(fallar)
    assert not breaker.abierto


def test_abrir_lo_abre_ya_el_tiempo_que_se_pida(monkeypatch):
    breaker = CircuitBreaker("prueba", umbral=5, enfriamiento=60)
    tiempos = []
    monkeypatch.setattr(cache, "set", lambda clave, valor, timeout: tiempos.append((clave, timeout)))

    breaker.abrir(7.4)
    breaker.abrir(0.2)  # nunca 0: en la caché de Django, timeout=0 es "caduca ya"

    assert tiempos == [("cb:prueba:abierto", 7), ("cb:prueba:abierto", 1)]


def test_abierto_a_mano_no_deja_pasar():
    breaker = CircuitBreaker("prueba", umbral=5, enfriamiento=60)
    breaker.abrir(30)
    with pytest.raises(CircuitoAbiertoException):
        breaker.llamar(lambda: "no llega")
