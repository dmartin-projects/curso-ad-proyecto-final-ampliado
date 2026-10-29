"""Módulo 95, ejercicios: dias_festivos (un servicio externo más, detrás de su port) y comparar_meses (una tool que
ahorra una vuelta), y el presupuesto de lo que ocupa el catálogo en cada llamada."""

import json
from datetime import date

import pytest

from asistente.application.tools.comparar_meses_tool import CompararMesesArgumentos, CompararMesesTool
from asistente.application.tools.dias_festivos_tool import DiasFestivosArgumentos, DiasFestivosTool
from asistente.domain.exceptions.servicio_externo_no_disponible_exception import ServicioExternoNoDisponibleException
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.read_models.festivo import Festivo
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.festivos_fake import FestivosFake
from asistente.tests.fakes.mundo import HOGAR, OCTUBRE, SEPTIEMBRE, Mundo, contexto
from core.domain.vo.mes import Mes

CALENDARIO = FestivosFake(
    [
        Festivo(date(2026, 5, 1), "Fiesta del Trabajo", ()),
        Festivo(date(2026, 5, 2), "Fiesta de la Comunidad de Madrid", ("ES-MD",)),
        Festivo(date(2026, 9, 11), "Diada Nacional de Catalunya", ("ES-CT",)),
    ]
)


def festivos(**args):
    return DiasFestivosTool(festivos=CALENDARIO).ejecutar(contexto(), DiasFestivosArgumentos(**args))


def test_festivos_nacionales_y_los_de_una_comunidad():
    assert festivos(comunidad="es-md") == {
        "anio": 2026,
        "hoy": "2026-10-29",
        "festivos": [
            {"fecha": "2026-05-01", "dia": "viernes", "nombre": "Fiesta del Trabajo", "ambito": "nacional"},
            {"fecha": "2026-05-02", "dia": "sábado", "nombre": "Fiesta de la Comunidad de Madrid", "ambito": "ES-MD"},
        ],
        "nota": "Nacionales y autonómicos. No incluye los locales de cada municipio (dos al año): si preguntan, dilo.",
    }
    assert [f["nombre"] for f in festivos()["festivos"]] == ["Fiesta del Trabajo"]


def test_festivos_solo_los_que_quedan():
    """Hoy es 29 de octubre (mundo.py): del calendario de arriba, ninguno. Y con uno en diciembre, solo ese."""
    assert festivos(comunidad="ES-MD", desde_hoy=True)["festivos"] == []
    navidad = Festivo(date(2026, 12, 25), "Navidad", ())
    tool = DiasFestivosTool(festivos=FestivosFake([*CALENDARIO.festivos, navidad]))
    r = tool.ejecutar(contexto(), DiasFestivosArgumentos(desde_hoy=True))
    assert [f["fecha"] for f in r["festivos"]] == ["2026-12-25"]


def test_festivos_argumentos_que_el_modelo_puede_corregir():
    tool = DiasFestivosTool(festivos=CALENDARIO)
    with pytest.raises(ToolException, match="«Madrid» no es un código de comunidad: usa ES-MD"):
        tool.validar('{"comunidad": "Madrid"}')
    with pytest.raises(ToolException, match="Solo hay festivos de 2021 a 2027"):
        festivos(anio=1990)


def test_festivos_sin_servicio_no_se_inventan():
    caido = FestivosFake(fallo=ServicioExternoNoDisponibleException("Nager.Date", "ConnectError"))
    with pytest.raises(ToolException, match="No los des de memoria"):
        DiasFestivosTool(festivos=caido).ejecutar(contexto(), DiasFestivosArgumentos())


def test_comparar_meses_de_la_que_mas_cambia_a_la_que_menos():
    mundo = Mundo()
    mundo.finanzas.resumenes = {
        (HOGAR, SEPTIEMBRE): resumen(SEPTIEMBRE, "776.59", categorias=[("Supermercado", "461.35"), ("Ocio", "82.99")]),
        (HOGAR, Mes(2026, 8)): resumen(
            Mes(2026, 8), "671.35", categorias=[("Supermercado", "474.75"), ("Casa", "88.30")]
        ),
    }
    r = CompararMesesTool(finanzas=mundo.finanzas).ejecutar(contexto(), CompararMesesArgumentos(mes="2026-09"))
    assert r == {
        "mes": "2026-09",
        "con": "2026-08",
        "gastos": {"mes": "776.59", "con": "671.35", "diferencia": "105.24"},
        "categorias": [
            {"categoria": "Casa", "mes": "0.00", "con": "88.30", "diferencia": "-88.30"},
            {"categoria": "Ocio", "mes": "82.99", "con": "0.00", "diferencia": "82.99"},
            {"categoria": "Supermercado", "mes": "461.35", "con": "474.75", "diferencia": "-13.40"},
        ],
    }


def test_comparar_meses_sin_mes_el_en_curso_con_el_anterior_y_nunca_consigo_mismo():
    tool = CompararMesesTool(finanzas=Mundo().finanzas)
    assert (tool.ejecutar(contexto(), CompararMesesArgumentos()))["con"] == str(SEPTIEMBRE)
    with pytest.raises(ToolException, match="el mismo mes"):
        tool.ejecutar(contexto(), CompararMesesArgumentos(mes=str(OCTUBRE), con=str(OCTUBRE)))


def test_cada_argumento_dice_lo_que_hace_sin_el():
    esquema = CompararMesesTool(finanzas=Mundo().finanzas).declaracion().parametros
    assert esquema["properties"]["con"]["description"].endswith("el anterior a 'mes'.")
    assert esquema["properties"]["mes"]["description"].endswith("el mes en curso del hogar.")


def test_la_prevision_dice_que_trae_el_total_del_mes_anterior():
    """Si la descripción no lo dice, el modelo lo pide a resumen_mes: una vuelta de más (§12.4 del módulo)."""
    from asistente.application.tools.prevision_fin_de_mes_tool import PrevisionFinDeMesTool

    assert "mes_anterior_total" in PrevisionFinDeMesTool(finanzas=Mundo().finanzas).descripcion


def test_el_catalogo_cabe_en_su_presupuesto():
    """Las declaraciones viajan en CADA llamada (medido en Groq: unos 420 tokens de entrada en la primera vuelta con 2
    tools, unos 1.300 con 11). Una descripción que crece sin control lo paga cada pregunta, y este test lo dice."""
    declaraciones = [t.declaracion() for t in Mundo().catalogo()]  # las 13
    caracteres = len(json.dumps([[d.nombre, d.descripcion, d.parametros] for d in declaraciones], ensure_ascii=False))
    assert caracteres <= 7_000, caracteres
