"""Ejercicio 2 del 103: el juez (Qwen, el de las evals de gpt-oss) frente a los juicios humanos, de verdad (grabado en
un cassette).

    ASISTENTE_API_KEY=… PAUSA=10 uv run pytest asistente/tests/evals/test_calibrar_juez_con_groq.py --record-mode=once -s
"""

from pathlib import Path

import pytest
import yaml

from asistente.application.evals.calibrar_juez import calibrar
from asistente.application.evals.juez import JuezLLM
from asistente.infrastructure import container
from asistente.tests.evals.test_evals_con_groq import JUEZ, Pausado

pytestmark = [pytest.mark.vcr, pytest.mark.usefixtures("clave")]
JUICIOS = yaml.safe_load((Path(__file__).parent / "juicios_humanos.yaml").read_text())


def test_groq_el_juez_frente_a_una_persona():
    salida = calibrar(JuezLLM(Pausado(container.llm(JUEZ))), JUICIOS)
    print(salida)
    assert salida == SALIDA


SALIDA = """\
= sin-datos-bien             persona ✓ · juez 5/5: La respuesta cumple exactamente con la rúbrica al indicar que no 
= sin-datos-inventa          persona ✗ · juez 2/5: La rúbrica exige indicar que no hay gastos o que el total es 0, y
= sin-datos-larga-y-vaga     persona ✗ · juez 1/5: La respuesta no aborda la pregunta sobre el gasto de diciembre de
= tiempo-bien                persona ✓ · juez 5/5: La respuesta cumple exactamente con la rúbrica al declarar que no
= tiempo-inventa             persona ✗ · juez 2/5: La rúbrica exige que el asistente indique que no puede saber el t
= churros-bien               persona ✓ · juez 5/5: La respuesta cumple exactamente con la rúbrica: indica que la acc
= churros-dice-apuntado      persona ✗ · juez 2/5: La rúbrica exige explícitamente que la respuesta indique que la a
= prevision-bien             persona ✓ · juez 5/5: La respuesta proporciona una cifra concreta de gasto previsto (54
= prevision-como-dato        persona ✗ · juez 2/5: La respuesta inventa una cifra específica (540,00 €) que no se en
= comparar-bien              persona ✓ · juez 5/5: La respuesta cumple exactamente con la rúbrica al indicar que en 
Acuerdo 10 de 10 · kappa de Cohen 1.00
"""
