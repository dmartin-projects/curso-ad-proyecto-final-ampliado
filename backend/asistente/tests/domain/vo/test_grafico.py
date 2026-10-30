"""Módulo 97: la especificación de un gráfico y sus datos."""

import pytest

from asistente.domain.enums.tipo_grafico import TipoGrafico
from asistente.domain.vo.especificacion_de_grafico import EspecificacionDeGrafico
from asistente.domain.vo.grafico import Grafico, Serie
from core.domain.exceptions.validacion_exception import ValidacionException


def test_la_especificacion_valida_tipo_y_titulo():
    e = EspecificacionDeGrafico("lineas", "  Gastos de 6 meses ", "tendencia", {"meses": 6})
    assert (e.tipo, e.titulo) == (TipoGrafico.LINEAS, "Gastos de 6 meses")
    with pytest.raises(ValueError):
        EspecificacionDeGrafico("tarta", "x", "tendencia")
    with pytest.raises(ValidacionException):
        EspecificacionDeGrafico("barras", "", "tendencia")


def test_cada_serie_un_valor_por_etiqueta():
    e = EspecificacionDeGrafico("barras", "x", "top_comercios")
    with pytest.raises(ValueError, match="un valor por etiqueta"):
        Grafico(e, ("a", "b"), (Serie("Gasto", (1.0,)),))


def test_el_resumen_para_el_modelo():
    e = EspecificacionDeGrafico("lineas", "x", "tendencia")
    g = Grafico(e, ("2026-08", "2026-09", "2026-10"), (Serie("Gastos", (0.0, 776.594, 505.14)),))
    assert g.resumen() == {
        "puntos": 3,
        "desde": "2026-08",
        "hasta": "2026-10",
        "series": [
            {
                "nombre": "Gastos",
                "total": 1281.73,
                "maximo": {"2026-09": 776.59},
                "minimo": {"2026-08": 0.0},
                "ultimo": {"2026-10": 505.14},
            }
        ],
    }
