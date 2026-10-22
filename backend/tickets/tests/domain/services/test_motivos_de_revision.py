"""Por qué un ticket va a revisión (módulo 88): lógica pura, sin base de datos."""

from datetime import date
from decimal import Decimal

import pytest

from tickets.domain.services.motivos_de_revision import motivos_de_revision
from tickets.domain.vo.datos_ticket import DatosTicket
from tickets.domain.vo.linea import Linea

HOY = date(2026, 10, 15)


def datos(**cambios):
    base = {"comercio": "Mercadona", "fecha": date(2026, 10, 12), "total": Decimal("4.85"), "confianza": 0.93}
    return DatosTicket(**base | cambios)


def test_sin_dudas_no_hay_motivos():
    assert motivos_de_revision(datos(), hoy=HOY, umbral=0.8) == []


@pytest.mark.parametrize(
    "cambios, motivo",
    [
        ({"confianza": 0.55}, "La IA no está segura (0.55)."),
        ({"total": None}, "No se ha encontrado el total."),
        ({"fecha": None}, "No se ha encontrado la fecha."),
        ({"fecha": date(2024, 1, 1)}, "La fecha no es plausible."),
        ({"fecha": date(2026, 10, 16)}, "La fecha no es plausible."),  # mañana: tampoco
        ({"comercio": ""}, "No se ha encontrado el comercio."),
        ({"lineas": (Linea("Leche", Decimal("2"), Decimal("0.95")),)}, "Las líneas suman 1.90 y el total es 4.85."),
    ],
)
def test_motivos_de_revision(cambios, motivo):
    assert motivos_de_revision(datos(**cambios), hoy=HOY, umbral=0.8) == [motivo]


def test_cinco_centimos_de_redondeo_no_son_un_motivo():
    lineas = (Linea("Leche", Decimal("2"), Decimal("0.95")), Linea("Pan", Decimal("1"), Decimal("2.99")))  # 4.89
    assert motivos_de_revision(datos(lineas=lineas), hoy=HOY, umbral=0.8) == []
