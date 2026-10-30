"""Módulo 93: los cassettes. Una llamada real a Groq se graba UNA vez (con la clave) y los tests la reproducen sin red.

    uv run pytest asistente                                          # sin red ni clave: reproduce los cassettes
    ASISTENTE_API_KEY=… uv run pytest asistente -k groq --record-mode=once   # graba los que falten

pytest-recording (vcrpy) intercepta el cliente HTTP del SDK. La cabecera Authorization NUNCA se graba, y la petición
tiene que coincidir byte a byte con la grabada (match_on con "body"): si cambia la traducción del adapter, el test
lo dice en vez de reproducir una respuesta a otra pregunta.
"""

import logging
import os
import re
from datetime import date
from decimal import Decimal

import pytest

from asistente.tests.fakes import casa as datos
from conftest import CategoriaFactory, CuentaFactory, HogarFactory, MembresiaFactory, MovimientoFactory, UsuarioFactory
from finanzas.models import Comercio

logging.getLogger("vcr").setLevel(logging.WARNING)  # en INFO, una línea (con el cuerpo entero) por petición


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": ["authorization", "cookie"],
        "before_record_response": _limpiar_respuesta,
        "match_on": ["method", "scheme", "host", "path", "query", "body"],
        "decode_compressed_response": True,
        "ignore_localhost": True,  # módulo 95: el servicio "caído" del test (127.0.0.1:9) no se graba, se cae de verdad
    }


def _limpiar_respuesta(respuesta: dict) -> dict:
    respuesta["headers"].pop("set-cookie", None)  # la cookie de Cloudflare: ni sirve ni tiene que estar en el repo
    respuesta["headers"].pop("Set-Cookie", None)
    cuerpo = respuesta["body"].get("string")
    if isinstance(cuerpo, bytes):  # el id de la organización de Groq (sale en los 429): no es de nadie más
        respuesta["body"]["string"] = re.sub(rb"org_[0-9a-z]+", b"org_...", cuerpo)
    elif isinstance(cuerpo, str):
        respuesta["body"]["string"] = re.sub(r"org_[0-9a-z]+", "org_...", cuerpo)
    return respuesta


@pytest.fixture
def clave(settings):
    """La clave real solo al grabar; al reproducir, cualquiera (no viaja: el cassette contesta)."""
    settings.ASISTENTE_API_KEY = os.environ.get("ASISTENTE_API_KEY") or "sin-clave-en-los-tests"
    settings.ASISTENTE_BASE_URL = "https://api.groq.com/openai/v1"
    settings.ASISTENTE_MODELO = "openai/gpt-oss-120b"


@pytest.fixture
def casa(db):
    """Un hogar con meses de datos FIJOS (fakes/casa.py: agosto, septiembre y octubre de 2026, hasta el 29, y septiembre
    de 2025): los resultados de las tools salen siempre iguales, y por eso la petición al LLM coincide byte a byte con
    la del cassette."""
    ana = UsuarioFactory(email="ana@example.com", nombre="Ana")
    hogar = HogarFactory(nombre=datos.NOMBRE)
    MembresiaFactory(hogar=hogar, usuario=ana, rol="admin")
    cuenta = CuentaFactory(hogar=hogar, nombre=datos.CUENTA)
    categorias = {}
    for nombre, padre, es_ingreso in datos.CATEGORIAS:
        categorias[nombre] = CategoriaFactory(
            hogar=hogar, nombre=nombre, padre=categorias.get(padre), es_ingreso=es_ingreso
        )
    comercios = {n: Comercio.objects.create(nombre=n) for n in datos.COMERCIOS}
    for fecha, importe, concepto, categoria, comercio in datos.MOVIMIENTOS:
        MovimientoFactory(
            cuenta=cuenta,
            fecha=date.fromisoformat(fecha),
            importe=Decimal(importe),
            concepto=concepto,
            categoria=categorias[categoria],
            comercio=comercios.get(comercio),
        )
    return ana, hogar
