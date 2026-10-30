"""Módulo 96, ejercicio 1: ¿se equivoca estimar_tokens hacia el lado bueno? Se comprueba con lo que contó Groq en
los cassettes: cada petición grabada lleva su texto y su respuesta, el `prompt_tokens` de verdad."""

import json
from pathlib import Path

import pytest
import yaml

from asistente.domain.services.tokens import estimar_tokens

# Todas las grabaciones del agente (módulo 97: también las del chat, con streaming: su uso va en el último trozo)
CASSETTES = sorted(Path(__file__).parents[2].rglob("cassettes/**/*.yaml"))


def peticiones():
    for cassette in CASSETTES:
        for interaccion in yaml.safe_load(cassette.read_text())["interactions"]:
            if "api.groq.com" not in interaccion["request"]["uri"]:
                continue  # Frankfurter, Eurostat, Nager
            cuerpo = json.loads(interaccion["request"]["body"])
            uso = _uso(interaccion["response"]["body"]["string"])
            if uso and cuerpo["model"].startswith("openai/gpt-oss") and not _con_cache(uso):
                # TODO lo que viaja: los mensajes, las tools y el schema del structured output (también se cuenta)
                enviado = [cuerpo["messages"], cuerpo.get("tools", []), cuerpo.get("response_format", {})]
                texto = json.dumps(enviado, ensure_ascii=False)
                yield cassette.stem, texto, uso["prompt_tokens"]


def _uso(respuesta: str) -> dict | None:
    """El `usage` de una respuesta: un JSON o, en streaming, el último trozo de los Server-Sent Events."""
    if not respuesta.startswith("data:"):
        return json.loads(respuesta).get("usage")
    trozos = [json.loads(x[5:]) for x in respuesta.split("\n") if x.startswith("data: {")]
    return next((t["usage"] for t in reversed(trozos) if t.get("usage")), None)


def _con_cache(uso: dict) -> bool:
    """Para calibrar, solo las respuestas sin caché: con caché, Groq puede devolver un `prompt_tokens` que no es lo que
    descuenta del límite por minuto (3.611 para una petición de unos 1.820). El coste sí sale siempre del `usage`."""
    return bool((uso.get("prompt_tokens_details") or {}).get("cached_tokens"))


MEDIDAS = list(peticiones())
# Lo que gpt-oss añade a CADA petición sin que viaje en el JSON: su plantilla (el formato "harmony": canales, roles,
# la fecha de corte…). En una petición pequeña se nota (un "¿Cuánto?" de 30 tokens llega como 87); en una de 3000, no.
# Medido en los cassettes del 93 y el 94: entre 40 y 60. No va en estimar_tokens: 60 tokens no cambian ningún presupuesto
# del agente, y así la estimación sigue siendo "del texto".
PLANTILLA = 60


def test_hay_medidas():
    assert MEDIDAS, "Ninguna petición a gpt-oss sin caché en los cassettes: no queda nada con qué calibrar"


@pytest.mark.parametrize("nombre, texto, reales", MEDIDAS, ids=[f"{m[0]}-{i}" for i, m in enumerate(MEDIDAS)])
def test_nunca_se_queda_corta_ni_se_pasa_del_doble(nombre, texto, reales):
    """Quedarse corto es lo peligroso (una petición que "cabía" y no cabe); pasarse, desperdiciar presupuesto."""
    estimados = estimar_tokens(texto)
    assert reales - PLANTILLA <= estimados <= 2 * reales, f"{nombre}: {estimados} estimados, {reales} reales"


def test_la_media_de_caracteres_por_token():
    """Lo que de verdad cuesta un token aquí, para elegir CARACTERES_POR_TOKEN con datos (y no con el 4 del inglés)."""
    caracteres = sum(len(t) for _, t, _ in MEDIDAS)
    tokens = sum(r for *_, r in MEDIDAS)
    assert 3.0 < caracteres / tokens < 6.0, caracteres / tokens
