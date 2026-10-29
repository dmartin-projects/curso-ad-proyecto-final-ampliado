"""Módulo 95: el periodo de las tools que buscan, con sus valores por defecto y errores que dicen qué hacer."""

from datetime import date

import pytest

from asistente.application.tools.periodo import periodo
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.tests.fakes.mundo import contexto


@pytest.mark.parametrize(
    "desde, hasta, esperado",
    [
        (None, None, (date(2026, 10, 1), date(2026, 10, 29))),  # el mes en curso, hasta hoy
        ("2026-08-01", None, (date(2026, 8, 1), date(2026, 10, 29))),
        (None, "2026-09-30", (date(2026, 9, 1), date(2026, 9, 30))),  # el mes de "hasta"
        ("2026-09-01", "2027-01-01", (date(2026, 9, 1), date(2026, 10, 29))),  # el futuro no tiene movimientos
    ],
)
def test_valores_por_defecto(desde, hasta, esperado):
    assert periodo(contexto(), desde, hasta) == esperado


@pytest.mark.parametrize(
    "desde, hasta, error",
    [
        (
            "2026-10-10",
            "2026-10-01",
            "'desde' \\(2026-10-10\\) es posterior a 'hasta' \\(2026-10-01; hoy es 2026-10-29\\)",
        ),
        ("2023-01-01", None, "pasa de dos años. Pide uno más corto o usa tendencia"),
    ],
)
def test_errores_que_dicen_que_hacer(desde, hasta, error):
    with pytest.raises(ToolException, match=error):
        periodo(contexto(), desde, hasta)
