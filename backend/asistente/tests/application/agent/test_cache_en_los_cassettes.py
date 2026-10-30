"""Módulo 99, ejercicio 3: el prompt caching de Groq, medido en lo que ya está grabado.

Una regla que tiene que cumplirse siempre (si no, el número de "cacheados" no significaría lo que creemos): la caché solo
puede cubrir algo que YA se envió. En cada pregunta grabada, lo cacheado de una llamada no pasa de lo que ocupaba la
llamada anterior más grande. Y una tabla, con -s, para ver cuánto se cachea vuelta a vuelta."""

import json
from collections import defaultdict

import pytest
import yaml

from asistente.tests.application.agent.test_calibrar_tokens import CASSETTES, _uso


def llamadas_por_cassette() -> dict[str, list[tuple[str, int, int]]]:
    """{cassette: [(modelo, prompt_tokens, cached_tokens)]} de las llamadas a Groq, en orden."""
    todas = defaultdict(list)
    for cassette in CASSETTES:
        for interaccion in yaml.safe_load(cassette.read_text())["interactions"]:
            if "api.groq.com" not in interaccion["request"]["uri"]:
                continue
            uso = _uso(interaccion["response"]["body"]["string"])
            if not uso:
                continue
            cacheados = (uso.get("prompt_tokens_details") or {}).get("cached_tokens") or 0
            modelo = json.loads(interaccion["request"]["body"])["model"]
            todas[cassette.stem].append((modelo, uso["prompt_tokens"], cacheados))
    return dict(todas)


LLAMADAS = llamadas_por_cassette()


@pytest.mark.parametrize("cassette", sorted(LLAMADAS))
def test_lo_cacheado_ya_se_habia_enviado(cassette):
    vistas: dict[str, int] = {}  # por modelo: cada modelo tiene su caché
    for modelo, entrada, cacheados in LLAMADAS[cassette]:
        assert cacheados <= entrada
        if modelo in vistas:  # la primera de cada modelo puede venir cacheada de otra grabación: no se comprueba
            assert cacheados <= vistas[modelo], f"{cassette}: {cacheados} cacheados y antes solo {vistas[modelo]}"
        vistas[modelo] = max(vistas.get(modelo, 0), entrada)


def test_la_tabla(capsys):
    filas = [(c, i + 1, e, k) for c, ls in sorted(LLAMADAS.items()) for i, (_, e, k) in enumerate(ls)]
    total, cacheados = sum(e for *_, e, _ in filas), sum(k for *_, k in filas)
    with capsys.disabled():
        print(f"\n{'grabación':<50} {'llamada':>7} {'entrada':>8} {'caché':>6}")
        for c, i, e, k in filas:
            print(f"{c[:50]:<50} {i:>7} {e:>8} {k:>6}")
        print(f"{'total':<50} {len(filas):>7} {total:>8} {cacheados:>6} ({cacheados / total:.0%})")
    assert total > 0
