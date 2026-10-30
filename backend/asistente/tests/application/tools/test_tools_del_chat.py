"""Módulo 97: las tools nuevas. Las de consulta (listar_cuentas, listar_miembros) y las del canal del chat, que
además del resultado para el modelo producen un artefacto para la interfaz (grafico, exportar, proponer_movimiento)."""

from datetime import date
from decimal import Decimal

import pytest

from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.exportar_tool import ExportarArgumentos
from asistente.application.tools.grafico_tool import GraficoArgumentos
from asistente.application.tools.listar_cuentas_tool import ListarCuentasTool
from asistente.application.tools.listar_miembros_tool import ListarMiembrosTool
from asistente.application.tools.proponer_movimiento_tool import ProponerMovimientoArgumentos
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.domain.enums.tipo_propuesta import TipoPropuesta
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.read_models.cuenta_del_hogar import CuentaDelHogar
from asistente.domain.read_models.mes_resumido import MesResumido
from asistente.domain.vo.archivo_exportado import ArchivoExportado
from asistente.domain.vo.grafico import Serie
from asistente.domain.vo.propuesta_preparada import PropuestaPreparada
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.mundo import HOGAR, OCTUBRE, SEPTIEMBRE, contexto
from core.domain.vo.mes import Mes


def tool(mundo, nombre):
    return next(t for t in mundo.catalogo(chat=True) if t.nombre == nombre)


def test_listar_cuentas_sin_iban_y_con_su_saldo(mundo):
    r = ListarCuentasTool(finanzas=mundo.finanzas).ejecutar(contexto(), SinArgumentos())
    assert r == {"cuentas": [{"nombre": "Cuenta común", "tipo": "banco", "saldo": "3853.12"}]}


def test_listar_miembros_sin_emails(mundo):
    r = ListarMiembrosTool(membresias=mundo.membresias).ejecutar(contexto(), SinArgumentos())
    assert r == {"miembros": [{"nombre": "Ana", "rol": "admin"}, {"nombre": "Luis", "rol": "miembro"}]}


def test_exportar_deja_el_archivo_fuera_del_modelo(mundo):
    r = tool(mundo, "exportar").ejecutar(contexto(), ExportarArgumentos(desde="2026-09-01", hasta="2026-09-30"))
    assert isinstance(r, ConArtefacto)
    assert r.para_el_modelo == {
        "archivo": "movimientos-2026-09-01-2026-09-30.csv",
        "filas": 12,
        "nota": "Listo: la interfaz enseña el enlace.",
    }
    assert isinstance(r.artefacto, ArchivoExportado) and r.artefacto.filas == 12
    actor, hogar_id, filtro, _ = mundo.exportador.pedidos[0]
    assert (hogar_id, filtro.desde, actor.rol) == (HOGAR, date(2026, 9, 1), "lector")  # con el Actor del agente


def test_exportar_sin_filas_no_ofrece_un_archivo_vacio(mundo):
    mundo.exportador.filas = 0
    r = tool(mundo, "exportar").ejecutar(contexto(), ExportarArgumentos(texto="nada"))
    assert r == {"filas": 0, "nota": "No hay movimientos con ese filtro: no se ha preparado ningún archivo."}


def test_grafico_vuelve_a_ejecutar_la_tool_de_datos(mundo):
    mundo.finanzas.resumenes[(HOGAR, OCTUBRE)] = resumen(
        OCTUBRE,
        evolucion=tuple(
            MesResumido(Mes(2026, m), Decimal(g), Decimal("2100"))
            for m, g in ((8, "671.35"), (9, "776.59"), (10, "505.14"))
        ),
    )
    args = GraficoArgumentos(tipo="lineas", titulo="Últimos 3 meses", fuente="tendencia", argumentos={"meses": 3})
    r = tool(mundo, "grafico").ejecutar(contexto(), args)
    # El modelo lee un resumen calculado aquí (no los puntos): con él comenta el gráfico sin inventar la tendencia
    assert r.para_el_modelo["puntos"] == 3
    assert r.para_el_modelo["series"][0] == {
        "nombre": "Gastos",
        "total": 1953.08,
        "maximo": {"2026-09": 776.59},
        "minimo": {"2026-10": 505.14},
        "ultimo": {"2026-10": 505.14},
    }
    g = r.artefacto
    assert g.etiquetas == ("2026-08", "2026-09", "2026-10")
    assert g.series == (Serie("Gastos", (671.35, 776.59, 505.14)), Serie("Ingresos", (2100.0, 2100.0, 2100.0)))


def test_grafico_con_argumentos_que_la_tool_de_datos_no_acepta(mundo):
    args = GraficoArgumentos(tipo="lineas", titulo="x", fuente="tendencia", argumentos={"meses": 40})
    with pytest.raises(ToolException, match="Argumentos no válidos para tendencia: meses"):
        tool(mundo, "grafico").ejecutar(contexto(), args)


def test_un_circular_tiene_una_serie(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(SEPTIEMBRE, "500", categorias=[("Ocio", "100")])
    args = GraficoArgumentos(tipo="circular", titulo="x", fuente="comparar_meses", argumentos={"mes": "2026-09"})
    with pytest.raises(ToolException, match="circular tiene una sola serie"):
        tool(mundo, "grafico").ejecutar(contexto(), args)


def test_proponer_movimiento_no_apunta_nada(mundo):
    args = ProponerMovimientoArgumentos(importe="3,5", concepto="Churros", categoria="ocio")
    r = tool(mundo, "proponer_movimiento").ejecutar(contexto(), args)
    assert r.para_el_modelo["nota"].startswith("Aún NO está apuntado")
    assert r.artefacto == PropuestaPreparada(
        TipoPropuesta.MOVIMIENTO,
        "Gasto de 3,50 €: «Churros», en Ocio, el 29/10/2026, en Cuenta común",
        {"cuenta_id": 1, "fecha": "2026-10-29", "importe": "-3.50", "concepto": "Churros", "categoria_id": 3},
    )


@pytest.mark.parametrize(
    "argumentos, error",
    [
        ('{"importe": "-3", "concepto": "x"}', "va en positivo"),
        ('{"importe": "3.333", "concepto": "x"}', "dos decimales"),
        ('{"importe": "tres", "concepto": "x"}', "no es un importe"),
    ],
)
def test_proponer_un_importe_que_no_vale(mundo, argumentos, error):
    with pytest.raises(ToolException, match=error):
        tool(mundo, "proponer_movimiento").validar(argumentos)


def test_proponer_en_el_futuro_o_sin_saber_la_cuenta(mundo):
    t = tool(mundo, "proponer_movimiento")
    with pytest.raises(ToolException, match="es futura"):
        t.ejecutar(contexto(), ProponerMovimientoArgumentos(importe="1", concepto="x", fecha="2026-11-02"))
    mundo.finanzas.cuentas_por_hogar[HOGAR] += (CuentaDelHogar(2, "Tarjeta", "tarjeta", True, Decimal(0)),)
    with pytest.raises(ToolException, match="¿En qué cuenta\\? Pregúntaselo al usuario: Cuenta común, Tarjeta"):
        t.ejecutar(contexto(), ProponerMovimientoArgumentos(importe="1", concepto="x"))
    r = t.ejecutar(
        contexto(), ProponerMovimientoArgumentos(importe="1", concepto="x", cuenta="tarjeta", tipo="ingreso")
    )
    assert (r.artefacto.datos["cuenta_id"], r.artefacto.datos["importe"]) == (2, "1.00")
