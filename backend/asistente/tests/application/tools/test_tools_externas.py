"""Módulo 95: tipo_de_cambio y comparar_con_ipc, sobre fakes de los servicios externos (sus adapters, en
tests/infrastructure/externos/). Lo importante: qué pasa cuando el servicio falla o el dato aún no existe."""

from datetime import date
from decimal import Decimal

import pytest

from asistente.application.tools.comparar_con_ipc_tool import CompararConIpcArgumentos, CompararConIpcTool
from asistente.application.tools.tipo_de_cambio_tool import TipoDeCambioArgumentos, TipoDeCambioTool
from asistente.domain.exceptions.moneda_desconocida_exception import MonedaDesconocidaException
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.read_models.serie_de_precios import SerieDePrecios
from asistente.tests.fakes.indice_de_precios_fake import IndiceDePreciosFake
from asistente.tests.fakes.mundo import contexto
from asistente.tests.fakes.tipo_de_cambio_fake import TipoDeCambioFake
from core.domain.vo.mes import Mes


def convertir(divisas, **args):
    return TipoDeCambioTool(divisas=divisas).ejecutar(contexto(), TipoDeCambioArgumentos(**args))


def test_a_la_moneda_del_hogar_con_el_tipo_del_dia_habil():
    divisas = TipoDeCambioFake({("GBP", "EUR"): ("1.1653", date(2026, 9, 11))})
    r = convertir(divisas, importe=Decimal("120"), de="gbp", fecha="2026-09-12")
    assert r == {
        "importe": "120.00 GBP",
        "resultado": "139.84 EUR",
        "tipo": "1 GBP = 1.1653 EUR",
        "fecha_del_tipo": "2026-09-11",
        "nota": "El BCE no publica en fines de semana ni festivos: es el del día hábil anterior.",
    }
    assert divisas.pedidos == [(Decimal("120"), "GBP", "EUR", date(2026, 9, 12))]


def test_si_el_servicio_no_responde_el_modelo_no_debe_inventar():
    divisas = TipoDeCambioFake(fallo=ServicioExternoNoDisponibleException("Frankfurter", "ReadTimeout"))
    with pytest.raises(ToolException, match="No des un tipo aproximado ni de memoria"):
        convertir(divisas, importe=Decimal("120"), de="GBP")


def test_una_moneda_desconocida_es_un_error_de_dominio_con_su_mensaje():
    with pytest.raises(MonedaDesconocidaException):  # el bucle le da al modelo su mensaje público
        convertir(TipoDeCambioFake(), importe=Decimal("1"), de="XXX")


def test_una_fecha_futura_ni_se_pregunta():
    divisas = TipoDeCambioFake()
    with pytest.raises(ToolException, match="La fecha 2026-11-02 es futura"):
        convertir(divisas, importe=Decimal("1"), de="USD", fecha="2026-11-02")
    assert divisas.pedidos == []


def ipc(precios, **args):
    from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake
    from asistente.tests.fakes.mundo import HOGAR

    tool = CompararConIpcTool(finanzas=ConsultasDeFinanzasFake.de_casa(HOGAR), precios=precios)
    return tool.ejecutar(contexto(), CompararConIpcArgumentos(**args))


def test_la_luz_frente_a_su_ipc():
    precios = IndiceDePreciosFake({"CP0451": SerieDePrecios("CP0451", "Electricity", {Mes(2026, 9): Decimal("11.4")})})
    r = ipc(precios, categoria="luz", mes="2026-09")
    assert r == {
        "categoria": "Luz",
        "mes": "2026-09",
        "grupo_ipc": "Electricidad",
        "gasto_hogar": "92.75",
        "gasto_hogar_un_anio_antes": "79.80",
        "variacion_hogar_pct": 16.2,
        "ipc_variacion_anual_pct": 11.4,
    }
    assert precios.pedidos == ["CP0451"]


def test_sin_mes_el_ultimo_cerrado_y_si_aun_no_esta_publicado_lo_dice():
    precios = IndiceDePreciosFake({"CP011": SerieDePrecios("CP011", "Food", {Mes(2026, 8): Decimal("4.6")})})
    r = ipc(precios, categoria="Supermercado")
    assert (r["mes"], r["ipc_variacion_anual_pct"]) == ("2026-09", None)
    assert r["nota_ipc"] == "El IPC de 2026-09 todavía no está publicado (el último es 2026-08)."


def test_sin_datos_del_anio_anterior_lo_dice():
    r = ipc(IndiceDePreciosFake(), categoria="Restaurantes", mes="2026-09")
    assert (r["variacion_hogar_pct"], r["nota_hogar"]) == (
        None,
        "No hay gastos de esta categoría en 2025-09: no se puede comparar.",
    )


def test_una_categoria_que_no_existe_dice_cuales_hay():
    with pytest.raises(
        ToolException,
        match="No hay ninguna categoría «Mascotas» en este hogar. Las que hay: Casa, Luz, Nómina, Ocio, Restaurantes, Supermercado, Transporte.",
    ):
        ipc(IndiceDePreciosFake(), categoria="Mascotas")


def test_un_mes_sin_terminar_no_se_compara():
    with pytest.raises(ToolException, match="2026-10 no ha terminado: compara un mes cerrado \\(hasta 2026-09\\)"):
        ipc(IndiceDePreciosFake(), categoria="Luz", mes="2026-10")


def test_si_eurostat_no_responde_el_modelo_no_debe_inventar():
    with pytest.raises(ToolException, match="No des una cifra de inflación de memoria"):
        ipc(IndiceDePreciosFake(fallo=ServicioExternoNoDisponibleException("Eurostat")), categoria="Luz", mes="2026-09")
