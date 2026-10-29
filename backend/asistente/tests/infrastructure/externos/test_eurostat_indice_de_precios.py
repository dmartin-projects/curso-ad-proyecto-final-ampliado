"""Módulo 95: el adapter de Eurostat (JSON-stat). Sin red para los casos raros; con un cassette, de verdad."""

from decimal import Decimal

import httpx
import pytest
import respx

from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.infrastructure.externos.eurostat_indice_de_precios import IndiceDePreciosEurostat
from core.domain.vo.mes import Mes

URL = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"


def json_stat(meses: dict[str, int], valores: dict[str, float], grupo="CP0451", nombre="Electricity (ND)") -> dict:
    """La forma de la respuesta de verdad (recortada): una serie, con la posición de cada mes en `time`."""
    return {
        "version": "2.0",
        "class": "dataset",
        "id": ["freq", "unit", "coicop18", "geo", "time"],
        "size": [1, 1, 1, 1, len(meses)],
        "value": valores,
        "dimension": {
            "coicop18": {"category": {"index": {grupo: 0}, "label": {grupo: nombre}}},
            "time": {"category": {"index": meses}},
        },
    }


def adapter() -> IndiceDePreciosEurostat:
    return IndiceDePreciosEurostat(base_url=URL, pausa=0)


@respx.mock
def test_lee_la_serie_y_un_mes_sin_valor_no_esta():
    ruta = respx.get(
        f"{URL}prc_hicp_minr", params={"geo": "ES", "unit": "RCH_A", "coicop18": "CP0451", "lastTimePeriod": "24"}
    )
    ruta.respond(json=json_stat({"2026-07": 0, "2026-08": 1, "2026-09": 2}, {"0": 8.3, "2": 11.4}))

    serie = adapter().serie("CP0451")

    assert serie.nombre == "Electricity (ND)"
    assert serie.tasas_anuales == {Mes(2026, 7): Decimal("8.3"), Mes(2026, 9): Decimal("11.4")}
    assert serie.ultimo_publicado == Mes(2026, 9)
    adapter().serie("CP0451")
    assert ruta.call_count == 1  # 12 horas en la caché: solo cambia cuando hay publicación nueva


@respx.mock
def test_un_grupo_sin_datos_es_una_serie_vacia():
    respx.get(f"{URL}prc_hicp_minr").respond(json=json_stat({"2026-09": 0}, {}, grupo="CPXX", nombre="CPXX"))
    assert adapter().serie("CPXX").ultimo_publicado is None


@respx.mock
@pytest.mark.parametrize("fallo", [httpx.Response(503), httpx.ConnectTimeout("lento")])
def test_si_no_responde(fallo):
    ruta = respx.get(f"{URL}prc_hicp_minr")
    ruta.mock(side_effect=fallo) if isinstance(fallo, Exception) else ruta.mock(return_value=fallo)
    with pytest.raises(ServicioExternoNoDisponibleException, match="Eurostat"):
        adapter().serie("CP0451")
    assert ruta.call_count == 2


@pytest.mark.vcr
def test_eurostat_de_verdad():
    """Grabado el 29-10-2026: el último mes publicado para España es septiembre (sale a mediados del mes siguiente)."""
    serie = adapter().serie("CP0451")
    assert serie.ultimo_publicado == Mes(2026, 9)
    assert serie.tasas_anuales[Mes(2026, 9)] == Decimal("11.4")
    assert len(serie.tasas_anuales) == 24
