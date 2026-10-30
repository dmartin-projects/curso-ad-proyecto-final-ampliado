"""Módulo 97: una propuesta se confirma una vez, y solo mientras está fresca."""

from datetime import UTC, datetime, timedelta

import pytest

from asistente.domain.bo.propuesta import Propuesta
from asistente.domain.enums.estado_propuesta import EstadoPropuesta
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from asistente.domain.exceptions.propuesta_ya_resuelta_exception import PropuestaYaResueltaException

CREADA = datetime(2026, 10, 29, 10, 0, tzinfo=UTC)


def propuesta() -> Propuesta:
    return Propuesta(1, 7, 3, TipoPropuesta.MOVIMIENTO, "Gasto de 3,50 €", {"importe": "-3.50"}, CREADA)


def test_se_confirma_una_vez():
    p = propuesta()
    p.confirmar({"movimiento_id": 9}, CREADA + timedelta(minutes=1))
    assert (p.estado, p.resultado) == (EstadoPropuesta.CONFIRMADA, {"movimiento_id": 9})
    with pytest.raises(PropuestaYaResueltaException, match="ya está confirmada"):
        p.confirmar({}, CREADA)
    with pytest.raises(PropuestaYaResueltaException):
        p.descartar()


def test_la_de_ayer_ha_caducado():
    with pytest.raises(PropuestaYaResueltaException, match="caducado"):
        propuesta().comprobar_pendiente(CREADA + timedelta(days=1, seconds=1))


def test_descartada_no_se_confirma():
    p = propuesta()
    p.descartar()
    with pytest.raises(PropuestaYaResueltaException, match="ya está descartada"):
        p.comprobar_pendiente(CREADA)
