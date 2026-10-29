"""Módulo 93, ejercicio 1: el structured output se valida como cualquier entrada externa (con LLMFake, sin red)."""

from datetime import date
from io import StringIO

import pytest
import time_machine
from django.core.management import call_command
from django.core.management.base import CommandError

from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.respuesta_llm import RespuestaLLM
from asistente.infrastructure import container
from asistente.tests.fakes.llm_fake import LLMFake


@pytest.fixture(autouse=True)
def hoy():
    with time_machine.travel(date(2026, 10, 29)):
        yield


def extraer(monkeypatch, respuesta: str | RespuestaLLM) -> tuple[str, LLMFake]:
    llm = LLMFake([LLMFake.responder(respuesta) if isinstance(respuesta, str) else respuesta])
    monkeypatch.setattr(container, "llm", lambda modelo=None: llm)
    salida = StringIO()
    call_command("probar_llm", "ayer pagué 23,40 en el Mercadona con la tarjeta", estructurado=True, stdout=salida)
    return salida.getvalue(), llm


def test_un_movimiento_valido_sale_normalizado(monkeypatch):
    salida, llm = extraer(
        monkeypatch, '{"concepto": "Mercadona", "importe": -23.399999, "fecha": "2026-10-28", "cuenta": "Tarjeta"}'
    )

    assert '{"concepto": "Mercadona", "importe": "-23.40", "fecha": "2026-10-28", "cuenta": "Tarjeta"}' in salida
    peticion = llm.peticiones[0]
    assert "Hoy es 2026-10-29" in peticion.sistema
    assert peticion.esquema.estricto
    assert peticion.esquema.esquema["required"] == ["concepto", "importe", "fecha", "cuenta"]
    assert peticion.esquema.esquema["additionalProperties"] is False
    assert "Ejercicio" not in str(peticion.esquema.esquema)  # nada de comentarios nuestros en lo que lee el modelo


def test_lo_que_no_se_sabe_es_null(monkeypatch):
    salida, _ = extraer(monkeypatch, '{"concepto": "Bar", "importe": -5, "fecha": null, "cuenta": null}')
    assert '"fecha": null, "cuenta": null' in salida


@pytest.mark.parametrize(
    "respuesta, error",
    [
        (
            '{"concepto": "Mercadona", "importe": 0, "fecha": null, "cuenta": null}',
            "importe: Value error, un movimiento no puede ser de 0 €",
        ),
        (
            '{"concepto": "Mercadona", "importe": -5, "fecha": "2026-11-02", "cuenta": null}',
            "fecha: Value error, la fecha está en el futuro",
        ),
        (
            '{"concepto": "Mercadona", "importe": -5, "fecha": null, "cuenta": "Visa Oro"}',
            "cuenta: Input should be 'Cuenta común', 'Tarjeta' or 'Efectivo'",
        ),
        (
            '{"concepto": "Mercadona", "importe": -5, "fecha": null, "cuenta": null, "nota": "x"}',
            "nota: Extra inputs are not permitted",
        ),
        (
            '{"concepto": "", "importe": -5, "fecha": null, "cuenta": null}',
            "concepto: String should have at least 1 character",
        ),
    ],
)
def test_lo_que_cumple_la_forma_pero_no_tiene_sentido_se_rechaza(monkeypatch, respuesta, error):
    with pytest.raises(CommandError, match=f"no ha devuelto un movimiento válido \\(fin\\): {error}"):
        extraer(monkeypatch, respuesta)


def test_un_json_cortado_por_max_tokens(monkeypatch):
    cortada = RespuestaLLM(Mensaje.modelo(texto='{"concepto": "Merca'), MotivoFin.LIMITE_TOKENS)
    with pytest.raises(CommandError, match=r"\(limite_tokens\): json: Invalid JSON"):
        extraer(monkeypatch, cortada)
