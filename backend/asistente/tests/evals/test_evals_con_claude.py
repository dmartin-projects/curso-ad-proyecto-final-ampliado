"""Módulo 106 (opcional, con cuenta de Anthropic): el mismo golden set del 103 con Claude (Haiku 5.5 y Sonnet 5.5),
juzgado por Qwen (otra familia), para compararlo con los de Groq (test_evals_con_groq.py, §8 del 103): aciertos por
categoría, tokens (con los leídos de la caché) y coste.

Con ANTHROPIC_API_KEY y ASISTENTE_API_KEY (la de Groq, para el juez) en el entorno, la primera vez se graba:

    uv run pytest asistente/tests/evals/test_evals_con_claude.py --record-mode=once -s

Cada test imprime su informe; copiado en SALIDA_HAIKU y SALIDA_SONNET, desde ahí se reproduce sin red ni clave.
Sin ANTHROPIC_API_KEY ni cassette, los dos se saltan con su motivo (no fallan): el CI sigue verde.
"""

import os
from pathlib import Path

import pytest

from asistente.tests.evals.test_evals_con_groq import golden

CASSETTES = Path(__file__).parent / "cassettes" / "test_evals_con_claude"


def grabado_o_con_clave(nombre: str):
    return pytest.mark.skipif(
        not (CASSETTES / f"{nombre}.yaml").exists() and not os.environ.get("ANTHROPIC_API_KEY"),
        reason="Opcional (módulo 106): sin ANTHROPIC_API_KEY ni cassette grabado; con tu clave, --record-mode=once -s",
    )


pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave"), pytest.mark.django_db]


@grabado_o_con_clave("test_claude_haiku")
def test_claude_haiku(casa):
    salida, _ = golden(casa, "claude-haiku-5-5")
    assert salida == SALIDA_HAIKU


@grabado_o_con_clave("test_claude_sonnet")
def test_claude_sonnet(casa):
    salida, _ = golden(casa, "claude-sonnet-5-5")
    assert salida == SALIDA_SONNET


SALIDA_HAIKU = ""
SALIDA_SONNET = ""
