"""Módulos 93 y 94: el composition root del asistente."""

from decimal import Decimal

import pytest
from django.core.exceptions import ImproperlyConfigured

from asistente.infrastructure import container
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM


def test_sin_clave_no_arranca(settings):
    settings.ASISTENTE_API_KEY = ""
    with pytest.raises(ImproperlyConfigured, match="Falta ASISTENTE_API_KEY"):
        container.llm()


def test_el_principal_con_su_reserva_o_solo_el_modelo_pedido(settings):
    settings.ASISTENTE_API_KEY, settings.ASISTENTE_MODELO = "clave", "openai/gpt-oss-120b"
    settings.ASISTENTE_MODELOS_RESERVA = ["openai/gpt-oss-20b"]

    llm = container.llm()
    assert isinstance(llm, LLMConReserva)
    assert [(m.modelo, c.clave_abierto) for m, c in llm.modelos] == [
        ("openai/gpt-oss-120b", "cb:llm:openai/gpt-oss-120b:abierto"),
        ("openai/gpt-oss-20b", "cb:llm:openai/gpt-oss-20b:abierto"),
    ]
    solo = container.llm("qwen/qwen3.8-27b")
    assert isinstance(solo, OpenAICompatibleLLM) and solo.modelo == "qwen/qwen3.8-27b"


def test_el_cliente_http_es_uno_por_configuracion(settings):
    settings.ASISTENTE_API_KEY = "clave"
    assert container.llm("a")._cliente is container.llm("b")._cliente  # la conexión se reutiliza


def test_precio_de_un_modelo_y_coste_desconocido(settings):
    settings.ASISTENTE_PRECIOS = {"openai/gpt-oss-120b": ("0.15", "0.60", "0.075")}

    assert container.precio("openai/gpt-oss-120b").salida == Decimal("0.60")
    assert container.precio("modelo-nuevo") is None


def test_el_agente_con_sus_tools_y_el_tiempo_de_los_ajustes(settings):
    settings.ASISTENTE_API_KEY, settings.ASISTENTE_SEGUNDOS_POR_PREGUNTA = "clave", 45
    agente = container.agente()
    assert list(agente.tools) == ["resumen_mes", "gasto_por_categoria"]
    assert (agente.limites.segundos, agente.limites.max_tokens) == (45, 10000)
