"""Módulos 93, 94 y 97: el composition root del asistente."""

from decimal import Decimal

import pytest
from django.core.exceptions import ImproperlyConfigured

from asistente.domain.enums.plan import Plan
from asistente.infrastructure import container
from asistente.infrastructure.llm.llm_con_reserva import LLMConReserva
from asistente.infrastructure.llm.openai_compatible_llm import OpenAICompatibleLLM
from asistente.infrastructure.tarifas.tarifas_desde_ajustes import TarifasDesdeAjustes
from asistente.infrastructure.telemetria.llm_medido import LLMMedido


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
    assert isinstance(solo, LLMMedido) and solo.modelo == "qwen/qwen3.8-27b"  # módulo 98: medido
    assert isinstance(solo.dentro, OpenAICompatibleLLM) and solo.servidor == "api.groq.com"


def test_el_cliente_http_es_uno_por_configuracion(settings):
    settings.ASISTENTE_API_KEY = "clave"
    assert container.llm("a").dentro._cliente is container.llm("b").dentro._cliente  # la conexión se reutiliza


def test_precio_de_un_modelo_y_coste_desconocido(settings):
    settings.ASISTENTE_PRECIOS = {"openai/gpt-oss-120b": ("0.15", "0.60", "0.075")}

    assert container.precio("openai/gpt-oss-120b").salida == Decimal("0.60")
    assert container.precio("modelo-nuevo") is None


def test_el_agente_con_sus_tools_y_el_tiempo_de_los_ajustes(settings):
    settings.ASISTENTE_API_KEY, settings.ASISTENTE_SEGUNDOS_POR_PREGUNTA = "clave", 45
    agente = container.agente()
    assert list(agente.tools) == [
        "resumen_mes",
        "gasto_por_categoria",
        "comparar_meses",
        "buscar_movimientos",
        "tendencia",
        "top_comercios",
        "estado_presupuestos",
        "prevision_fin_de_mes",
        "listar_categorias",
        "detalle_ticket",
        "tipo_de_cambio",
        "comparar_con_ipc",
        "dias_festivos",
        "listar_cuentas",
        "listar_miembros",
    ]
    assert (agente.limites.segundos, agente.limites.max_tokens) == (45, 10000)


def test_el_chat_ademas_con_las_de_su_canal(settings):
    """Módulo 97: gráficos, archivos y propuestas solo en el chat (la terminal no los puede enseñar)."""
    settings.ASISTENTE_API_KEY = "clave"
    consulta, chat = list(container.agente().tools), list(container.agente(chat=True).tools)
    assert chat == [*consulta, "grafico", "exportar", "proponer_movimiento"]


def test_el_modelo_auxiliar_con_el_principal_de_reserva(settings):
    settings.ASISTENTE_API_KEY, settings.ASISTENTE_MODELO = "clave", "openai/gpt-oss-120b"
    settings.ASISTENTE_MODELO_AUXILIAR = "openai/gpt-oss-20b"
    assert [m.modelo for m, _ in container.llm_auxiliar().modelos] == ["openai/gpt-oss-20b", "openai/gpt-oss-120b"]


def test_cada_plan_tiene_su_cuota_en_los_ajustes():  # módulo 98: un plan sin cuota sería un KeyError en producción
    for plan in Plan:
        assert TarifasDesdeAjustes().cuota(plan).tokens_dia_persona > 0
