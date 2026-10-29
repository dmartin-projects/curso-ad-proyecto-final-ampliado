"""Módulo 96: los prompts, como código. Tres comprobaciones que no necesitan un LLM:

1. nadie cambia el texto sin cambiar la versión (la huella del texto es la registrada para su versión);
2. el prompt de un día y un hogar concretos es EXACTAMENTE el del archivo de referencia (golden file): un cambio se
   ve entero en el pull request, con su diff;
3. lo que depende de la fecha se calcula bien también en los bordes del año.
"""

import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from asistente.application.agent.instrucciones import instrucciones
from asistente.application.prompts.estructura import ESTRUCTURA
from asistente.application.prompts.sistema import SISTEMA
from asistente.application.prompts.versiones import PUBLICADAS
from asistente.domain.services.tokens import estimar_tokens
from asistente.tests.fakes.mundo import contexto

REFERENCIA = Path(__file__).with_name("sistema.txt")


@pytest.mark.parametrize("plantilla", [SISTEMA, ESTRUCTURA], ids=lambda p: p.nombre)
def test_cambiar_el_texto_obliga_a_publicar_una_version(plantilla):
    assert PUBLICADAS.get((plantilla.nombre, plantilla.version)) == plantilla.huella, (
        f"El texto de «{plantilla.nombre}» ha cambiado: sube su versión y añádela a prompts/versiones.py "
        f"con la huella {plantilla.huella} (y vuelve a grabar los cassettes)."
    )


def test_el_prompt_de_un_dia_es_el_de_referencia():
    """Si cambias el prompt a propósito: REGENERAR=1 uv run pytest … reescribe el archivo, y el diff va al PR."""
    texto = instrucciones(contexto())
    if os.environ.get("REGENERAR"):
        REFERENCIA.write_text(texto + "\n")
    assert texto + "\n" == REFERENCIA.read_text()


def test_cabe_en_su_presupuesto():
    """Se paga en CADA llamada: unos 400 tokens estimados (medido en Groq: el system prompt de este módulo añade
    unas 250 a la primera vuelta frente al del 94)."""
    assert estimar_tokens(instrucciones(contexto())) <= 450


@pytest.mark.parametrize(
    "ahora, esperado",
    [
        (datetime(2027, 1, 15, 12, tzinfo=UTC), "«diciembre» es 2026-12 y «febrero», 2026-02"),
        (datetime(2026, 12, 31, 12, tzinfo=UTC), "«noviembre» es 2026-11 y «enero», 2026-01"),
        # 23:30 en UTC del 31 de octubre es ya 1 de noviembre en Madrid: manda la zona del HOGAR
        (datetime(2026, 10, 31, 23, 30, tzinfo=UTC), "«octubre» es 2026-10 y «diciembre», 2025-12"),
    ],
)
def test_los_meses_sin_anio_en_los_bordes(ahora, esperado):
    assert esperado in instrucciones(contexto(ahora=ahora))
