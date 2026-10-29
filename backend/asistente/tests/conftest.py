"""Módulo 93: los cassettes. Una llamada real a Groq se graba UNA vez (con la clave) y los tests la reproducen sin red.

    uv run pytest asistente                                          # sin red ni clave: reproduce los cassettes
    ASISTENTE_API_KEY=… uv run pytest asistente -k groq --record-mode=once   # graba los que falten

pytest-recording (vcrpy) intercepta el cliente HTTP del SDK. La cabecera Authorization NUNCA se graba, y la petición
tiene que coincidir byte a byte con la grabada (match_on con "body"): si cambia la traducción del adapter, el test
lo dice en vez de reproducir una respuesta a otra pregunta.
"""

import logging
import os

import pytest

logging.getLogger("vcr").setLevel(logging.WARNING)  # en INFO, una línea (con el cuerpo entero) por petición


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization", "cookie"],
        "before_record_response": _sin_cookies,
        "match_on": ["method", "scheme", "host", "path", "query", "body"],
        "decode_compressed_response": True,
    }


def _sin_cookies(respuesta: dict) -> dict:
    respuesta["headers"].pop("set-cookie", None)  # la cookie de Cloudflare: ni sirve ni tiene que estar en el repo
    respuesta["headers"].pop("Set-Cookie", None)
    return respuesta


@pytest.fixture
def clave(settings):
    """La clave real solo al grabar; al reproducir, cualquiera (no viaja: el cassette contesta)."""
    settings.ASISTENTE_API_KEY = os.environ.get("ASISTENTE_API_KEY") or "sin-clave-en-los-tests"
    settings.ASISTENTE_BASE_URL = "https://api.groq.com/openai/v1"
    settings.ASISTENTE_MODELO = "openai/gpt-oss-120b"
