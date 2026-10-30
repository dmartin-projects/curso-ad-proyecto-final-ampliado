"""Módulo 98: la cuota de un plan y el estado de quien pregunta."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from asistente.domain.enums.plan import Plan
from asistente.domain.exceptions.cuota_agotada_exception import CuotaAgotadaException
from asistente.domain.vo.cuota import Cuota
from asistente.domain.vo.estado_de_cuota import EstadoDeCuota

CUOTA = Cuota(tokens_dia_persona=1000, coste_mes_hogar=Decimal("0.50"))
AHORA = datetime(2026, 10, 29, 22, 0, tzinfo=UTC)
MANANA = datetime(2026, 10, 29, 23, 0, tzinfo=UTC)  # las 00:00 del 30 en Madrid (UTC+1 desde el domingo)
MES = datetime(2026, 10, 31, 23, 0, tzinfo=UTC)


def estado(tokens=0, coste="0") -> EstadoDeCuota:
    return EstadoDeCuota(Plan.BASICO, CUOTA, tokens, Decimal(coste), MANANA, MES)


def test_una_cuota_sin_margen_no_es_una_cuota():
    with pytest.raises(ValueError):
        Cuota(tokens_dia_persona=0, coste_mes_hogar=Decimal("1"))


def test_por_debajo_se_pregunta():
    e = estado(tokens=999, coste="0.49")
    e.exigir(AHORA)
    assert e.tokens_restantes == 1


def test_la_persona_ha_llegado_al_limite_del_dia():
    with pytest.raises(CuotaAgotadaException) as e:
        estado(tokens=1000).exigir(AHORA)
    assert e.value.status == 429 and e.value.contexto["segundos"] == 3600
    assert "Mañana" in e.value.mensaje


def test_el_hogar_manda_sobre_la_persona():
    """Si el hogar no tiene, da igual lo que le quede a la persona: el mensaje es el del mes."""
    with pytest.raises(CuotaAgotadaException, match="este mes") as e:
        estado(tokens=1000, coste="0.50").exigir(AHORA)
    assert e.value.contexto["renueva"] == MES.isoformat()
