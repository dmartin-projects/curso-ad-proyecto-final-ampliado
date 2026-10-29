"""Módulo 95, ejercicio 1: el adapter de Nager.Date. Sin red para los casos raros; con un cassette, de verdad."""

from datetime import date

import httpx
import pytest
import respx

from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.read_models.festivo import Festivo
from asistente.infrastructure.externos.nager_festivos import FestivosNager

URL = "https://date.nager.at/api/v3/"


def adapter() -> FestivosNager:
    return FestivosNager(base_url=URL, pausa=0)


def festivo(fecha, nombre, comunidades=None, tipos=("Public",)) -> dict:
    return {
        "date": fecha,
        "localName": nombre,
        "counties": comunidades,
        "global": not comunidades,
        "types": list(tipos),
    }


@respx.mock
def test_solo_los_festivos_de_verdad_y_a_la_cache():
    ruta = respx.get(f"{URL}PublicHolidays/2026/ES").respond(
        json=[
            festivo("2026-05-01", "Fiesta del Trabajo"),
            festivo("2026-05-02", "Fiesta de la Comunidad de Madrid", ["ES-MD"]),
            festivo("2026-12-24", "Nochebuena", tipos=("Bank",)),
        ]
    )
    esperado = (
        Festivo(date(2026, 5, 1), "Fiesta del Trabajo", ()),
        Festivo(date(2026, 5, 2), "Fiesta de la Comunidad de Madrid", ("ES-MD",)),
    )
    assert adapter().del_anio(2026, "ES") == esperado
    assert adapter().del_anio(2026, "ES") == esperado
    assert ruta.call_count == 1


@respx.mock
def test_si_no_responde():
    ruta = respx.get(f"{URL}PublicHolidays/2026/ES").mock(side_effect=httpx.ConnectError("caído"))
    with pytest.raises(ServicioExternoNoDisponibleException, match="Nager"):
        adapter().del_anio(2026, "ES")
    assert ruta.call_count == 2


@pytest.mark.vcr
def test_nager_de_verdad():
    """Grabado el 29-10-2026."""
    festivos = adapter().del_anio(2026, "ES")
    assert Festivo(date(2026, 5, 2), "Fiesta de la Comunidad de Madrid", ("ES-MD",)) in festivos
    assert sum(f.nacional for f in festivos) >= 8
