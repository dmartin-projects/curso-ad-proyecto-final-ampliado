"""Módulo 94: la reserva de modelos y el circuit breaker por modelo, con LLMFake y la caché de los tests."""

import pytest

from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException
from asistente.domain.exceptions.peticion_llm_exception import PeticionLLMException
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.tests.fakes.llm_fake import LLMFake
from core.infrastructure.cache.circuit_breaker import CircuitBreaker

PETICION = PeticionLLM(sistema="", mensajes=(Mensaje.usuario("hola"),))


def reserva(principal: list, segundo: list) -> tuple[LLMConReserva, LLMFake, LLMFake, CircuitBreaker]:
    a, b = LLMFake(principal, modelo="grande"), LLMFake(segundo, modelo="pequeño")
    circuito = CircuitBreaker("llm:grande", umbral=3, enfriamiento=120)
    return (
        LLMConReserva([(a, circuito), (b, CircuitBreaker("llm:pequeño", umbral=3, enfriamiento=120))]),
        a,
        b,
        circuito,
    )


def test_contesta_el_principal_si_puede():
    llm, _, segundo, _ = reserva([LLMFake.responder("hola", modelo="grande")], [])
    assert (llm.modelo, llm.generar(PETICION).modelo, segundo.peticiones) == ("grande", "grande", [])


def test_si_el_principal_no_esta_disponible_contesta_la_reserva():
    llm, _, _, circuito = reserva(
        [LLMNoDisponibleException("grande: 503")], [LLMFake.responder("hola", modelo="pequeño")]
    )
    assert llm.generar(PETICION).modelo == "pequeño"
    assert not circuito.abierto  # un fallo no basta para abrirlo (umbral 3)


def test_un_429_deja_fuera_al_principal_lo_que_pida_el_proveedor(monkeypatch):
    abiertos = []
    monkeypatch.setattr(CircuitBreaker, "abrir", lambda self, segundos: abiertos.append((self.clave_abierto, segundos)))
    llm, principal, _, _ = reserva(
        [LLMNoDisponibleException("grande: 429", reintentar_en=7.0)], [LLMFake.responder("hola", modelo="pequeño")]
    )
    assert llm.generar(PETICION).modelo == "pequeño"
    assert abiertos == [("cb:llm:grande:abierto", 7.0)]


def test_con_el_circuito_abierto_ni_se_intenta():
    llm, principal, _, circuito = reserva([], [LLMFake.responder("1"), LLMFake.responder("2")])
    circuito.abrir(60)
    llm.generar(PETICION)
    llm.generar(PETICION)
    assert principal.peticiones == []  # ni una: se ahorra sus reintentos y su timeout en cada pregunta


def test_tres_fallos_seguidos_abren_el_circuito():
    llm, principal, _, circuito = reserva(
        [LLMNoDisponibleException("503")] * 3, [LLMFake.responder(str(i)) for i in range(4)]
    )
    for _ in range(4):
        llm.generar(PETICION)
    assert circuito.abierto
    assert len(principal.peticiones) == 3  # la cuarta pregunta ya no lo intentó


def test_un_error_de_la_peticion_no_pasa_al_siguiente_ni_abre_el_circuito():
    llm, _, segundo, circuito = reserva([PeticionLLMException("400 schema")] * 3, [])
    for _ in range(3):
        with pytest.raises(PeticionLLMException, match="400 schema"):
            llm.generar(PETICION)
    assert segundo.peticiones == [] and not circuito.abierto


def test_si_ninguno_esta_disponible_el_ultimo_error():
    llm, *_ = reserva([LLMNoDisponibleException("grande: 503")], [LLMNoDisponibleException("pequeño: 429", 30)])
    with pytest.raises(LLMNoDisponibleException, match="pequeño: 429"):
        llm.generar(PETICION)


def test_hace_falta_un_modelo():
    with pytest.raises(ValueError, match="al menos un modelo"):
        LLMConReserva([])
