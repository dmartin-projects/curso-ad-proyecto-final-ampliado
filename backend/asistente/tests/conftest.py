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
    """Un hogar con tres meses de datos FIJOS (agosto, septiembre y octubre de 2026, hasta el 29): los resultados de
    las tools salen siempre iguales, y por eso la petición al LLM coincide byte a byte con la del cassette."""
    ana = UsuarioFactory(email="ana@example.com", nombre="Ana")
    hogar = HogarFactory(nombre="Casa de Ana y Luis")
    MembresiaFactory(hogar=hogar, usuario=ana, rol="admin")
    cuenta = CuentaFactory(hogar=hogar, nombre="Cuenta común")
    super_ = CategoriaFactory(hogar=hogar, nombre="Supermercado")
    restaurantes = CategoriaFactory(hogar=hogar, nombre="Restaurantes")
    ocio = CategoriaFactory(hogar=hogar, nombre="Ocio")
    casa_ = CategoriaFactory(hogar=hogar, nombre="Casa")
    luz = CategoriaFactory(hogar=hogar, nombre="Luz", padre=casa_)
    transporte = CategoriaFactory(hogar=hogar, nombre="Transporte")
    nomina = CategoriaFactory(hogar=hogar, nombre="Nómina")
    comercios = {n: Comercio.objects.create(nombre=n) for n in ("Mercadona", "Lidl", "Bar Manolo", "Netflix", "Renfe")}

    def mov(fecha, importe, concepto, categoria, comercio=None):
        MovimientoFactory(
            cuenta=cuenta,
            fecha=date.fromisoformat(fecha),
            importe=Decimal(importe),
            concepto=concepto,
            categoria=categoria,
            comercio=comercios.get(comercio),
        )

    for mes in ("08", "09", "10"):
        mov(f"2026-{mes}-01", "2100.00", "Nómina", nomina)
        mov(f"2026-{mes}-02", "-37.50", "Abono transporte", transporte, "Renfe")
    for fecha, importe, concepto, categoria, comercio in [
        ("2026-08-03", "-312.40", "Compra semanal", super_, "Mercadona"),
        ("2026-08-17", "-98.15", "Compra", super_, "Mercadona"),
        ("2026-08-10", "-64.20", "Compra", super_, "Lidl"),
        ("2026-08-14", "-46.80", "Cena", restaurantes, "Bar Manolo"),
        ("2026-08-22", "-24.00", "Cine", ocio, None),
        ("2026-08-28", "-88.30", "Factura de la luz", luz, None),
        ("2026-09-05", "-287.90", "Compra semanal", super_, "Mercadona"),
        ("2026-09-19", "-121.35", "Compra", super_, "Mercadona"),
        ("2026-09-12", "-52.10", "Compra", super_, "Lidl"),
        ("2026-09-13", "-23.40", "Cena (a medias)", restaurantes, "Bar Manolo"),
        ("2026-09-20", "-78.60", "Cumpleaños de Luis", restaurantes, None),
        ("2026-09-15", "-17.99", "Suscripción", ocio, "Netflix"),
        ("2026-09-26", "-65.00", "Concierto", ocio, None),
        ("2026-09-28", "-92.75", "Factura de la luz", luz, None),
        ("2026-10-03", "-301.25", "Compra semanal", super_, "Mercadona"),
        ("2026-10-11", "-45.80", "Compra", super_, "Lidl"),
        ("2026-10-18", "-31.20", "Cena", restaurantes, "Bar Manolo"),
        ("2026-10-15", "-17.99", "Suscripción", ocio, "Netflix"),
        ("2026-10-27", "-71.40", "Factura de la luz", luz, None),
    ]:
        mov(fecha, importe, concepto, categoria, comercio)
    return ana, hogar
