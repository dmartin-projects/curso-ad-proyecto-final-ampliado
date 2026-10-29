"""Módulo 93: el composition root del asistente."""

from decimal import Decimal

import pytest
from django.core.exceptions import ImproperlyConfigured

from asistente.infrastructure import container
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM


def test_sin_clave_no_arranca(settings):
    settings.ASISTENTE_API_KEY = ""
    with pytest.raises(ImproperlyConfigured, match="Falta ASISTENTE_API_KEY"):
        container.llm()


def test_monta_el_adapter_con_el_modelo_de_los_ajustes_o_el_pedido(settings):
    settings.ASISTENTE_API_KEY, settings.ASISTENTE_MODELO = "clave", "openai/gpt-oss-120b"

    assert isinstance(container.llm(), OpenAICompatibleLLM)
    assert container.llm().modelo == "openai/gpt-oss-120b"
    assert container.llm("openai/gpt-oss-20b").modelo == "openai/gpt-oss-20b"


def test_el_cliente_http_es_uno_por_configuracion(settings):
    settings.ASISTENTE_API_KEY = "clave"
    assert container.llm()._cliente is container.llm("openai/gpt-oss-20b")._cliente  # la conexión se reutiliza


def test_precio_de_un_modelo_y_coste_desconocido(settings):
    settings.ASISTENTE_PRECIOS = {"openai/gpt-oss-120b": ("0.15", "0.60", "0.075")}

    assert container.precio("openai/gpt-oss-120b").salida == Decimal("0.60")
    assert container.precio("modelo-nuevo") is None
