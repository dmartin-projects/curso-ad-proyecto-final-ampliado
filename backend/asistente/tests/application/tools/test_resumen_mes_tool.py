"""Módulo 94: resumen_mes, sobre el fake de finanzas."""

import pytest

from asistente.application.tools.resumen_mes_tool import ResumenMesArgumentos, ResumenMesTool
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.tests.fakes.consultas_de_finanzas_fake import ConsultasDeFinanzasFake, resumen
from asistente.tests.fakes.mundo import HOGAR, OCTUBRE, SEPTIEMBRE, contexto


@pytest.fixture
def finanzas():
    return ConsultasDeFinanzasFake(
        {
            (HOGAR, SEPTIEMBRE): resumen(SEPTIEMBRE, gastos="1116", ingresos="2100", num=40, anterior="1240"),
            (HOGAR, OCTUBRE): resumen(OCTUBRE, gastos="642.15", num=22, anterior="1116", pendientes=3),
        }
    )


def test_un_mes_cerrado(finanzas):
    r = ResumenMesTool(finanzas=finanzas).ejecutar(contexto(), ResumenMesArgumentos(mes="2026-09"))
    assert r == {
        "mes": "2026-09",
        "gastos": "1116.00",
        "ingresos": "2100.00",
        "balance": "984.00",
        "movimientos": 40,
        "gastos_mes_anterior": "1240.00",
        "variacion_gastos_pct": -10.0,
    }


def test_sin_mes_el_mes_en_curso_del_hogar_y_avisa_de_que_no_ha_terminado(finanzas):
    r = ResumenMesTool(finanzas=finanzas).ejecutar(contexto(), ResumenMesArgumentos())
    assert (r["mes"], r["mes_en_curso"], r["movimientos_sin_revisar"]) == ("2026-10", "hasta el día 29", 3)


def test_un_mes_futuro_es_un_error_que_dice_que_hacer(finanzas):
    with pytest.raises(ToolException, match="El mes 2027-01 todavía no ha empezado"):
        ResumenMesTool(finanzas=finanzas).ejecutar(contexto(), ResumenMesArgumentos(mes="2027-01"))
    assert finanzas.consultas == []
