"""Módulo 94: la reserva de verdad. Dos preguntas grandes seguidas agotan los 8.000 tokens por minuto de gpt-oss-120b en
la capa gratuita de Groq: la segunda recibe un 429 con retry-after y la contesta gpt-oss-20b (otra cuota). La tercera
ya no intenta el principal: su circuito está abierto. Grabado en un cassette."""

import logging

import pytest

from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.infrastructure import container

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave")]

MOVIMIENTOS = "Movimiento: 12,30 € en Mercadona el 3 de septiembre. " * 300  # unos 4.900 tokens


def pregunta(texto: str) -> PeticionLLM:
    return PeticionLLM(
        sistema="", mensajes=(Mensaje.usuario(texto),), esfuerzo=EsfuerzoDeRazonamiento.BAJO, max_tokens=300
    )


def test_groq_un_429_y_contesta_la_reserva(settings, caplog):
    settings.ASISTENTE_MODELOS_RESERVA = ["openai/gpt-oss-20b"]
    llm = container.llm()
    grande = pregunta(MOVIMIENTOS + "\n¿Cuántos movimientos hay? Solo el número.")

    with caplog.at_level(logging.INFO, logger="asistente.infrastructure.llm.llm_con_reserva"):
        modelos = [llm.generar(grande).modelo, llm.generar(grande).modelo]
        modelos.append(llm.generar(pregunta("¿Cuánto son 12,30 € por 300? Solo el número.")).modelo)

    print("\n".join(caplog.messages))
    assert modelos == ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "openai/gpt-oss-20b"]
    assert caplog.messages[0].startswith(
        "LLM no disponible (openai/gpt-oss-120b: 429 rate_limit_exceeded Rate limit reached for model "
        "`openai/gpt-oss-120b` in organization `org_...`"
    )
    assert caplog.messages[1] == "LLM openai/gpt-oss-120b con el circuito abierto; pruebo el siguiente"
