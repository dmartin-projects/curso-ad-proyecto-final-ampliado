"""Módulo 95: las tools que leen el dashboard (top_comercios, estado_presupuestos, tendencia, prevision_fin_de_mes)."""

from datetime import date
from decimal import Decimal

from asistente.application.tools.estado_presupuestos_tool import EstadoPresupuestosArgumentos, EstadoPresupuestosTool
from asistente.application.tools.prevision_fin_de_mes_tool import PrevisionFinDeMesTool
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tendencia_tool import TendenciaArgumentos, TendenciaTool
from asistente.application.tools.top_comercios_tool import TopComerciosArgumentos, TopComerciosTool
from asistente.domain.read_models.estado_de_presupuesto import EstadoDePresupuesto
from asistente.domain.read_models.gasto_de_comercio import GastoDeComercio
from asistente.domain.read_models.gasto_del_dia import GastoDelDia
from asistente.domain.read_models.mes_resumido import MesResumido
from asistente.tests.fakes.consultas_de_finanzas_fake import resumen
from asistente.tests.fakes.mundo import HOGAR, OCTUBRE, SEPTIEMBRE, contexto
from core.domain.vo.mes import Mes


def test_top_comercios(mundo):
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(
        SEPTIEMBRE, top_comercios=(GastoDeComercio("Mercadona", Decimal("409.25"), 2),)
    )
    r = TopComerciosTool(finanzas=mundo.finanzas).ejecutar(contexto(), TopComerciosArgumentos(mes="2026-09"))
    assert r == {"mes": "2026-09", "comercios": [{"comercio": "Mercadona", "total": "409.25", "veces": 2}]}


def test_presupuestos_con_su_estado_y_el_mes_en_curso(mundo):
    mundo.finanzas.resumenes[(HOGAR, OCTUBRE)] = resumen(
        OCTUBRE,
        presupuestos=(
            EstadoDePresupuesto("Supermercado", Decimal("400"), Decimal("347.05"), 86),
            EstadoDePresupuesto("Ocio", Decimal("50"), Decimal("17.99"), 35),
            EstadoDePresupuesto("Restaurantes", Decimal("25"), Decimal("31.20"), 124),
        ),
    )
    r = EstadoPresupuestosTool(finanzas=mundo.finanzas).ejecutar(contexto(), EstadoPresupuestosArgumentos())
    assert [(p["categoria"], p["estado"]) for p in r["presupuestos"]] == [
        ("Supermercado", "cerca"),
        ("Ocio", "bien"),
        ("Restaurantes", "superado"),
    ]
    assert r["presupuestos"][0] == {
        "categoria": "Supermercado",
        "limite": "400.00",
        "gastado": "347.05",
        "porcentaje": 86,
        "estado": "cerca",
    }
    assert r["mes_en_curso"] == "hasta el día 29"


def test_sin_presupuestos_lo_dice(mundo):
    r = EstadoPresupuestosTool(finanzas=mundo.finanzas).ejecutar(
        contexto(), EstadoPresupuestosArgumentos(mes="2026-09")
    )
    assert r == {"mes": "2026-09", "presupuestos": [], "nota": "El hogar no tiene presupuestos en 2026-09."}


def test_tendencia_de_una_vez_con_la_media_de_los_meses_cerrados(mundo):
    evolucion = tuple(
        MesResumido(Mes(2026, m), Decimal(g), Decimal("2100"))
        for m, g in [(7, "900"), (8, "671.35"), (9, "776.59"), (10, "504.94")]
    )
    mundo.finanzas.resumenes[(HOGAR, OCTUBRE)] = resumen(OCTUBRE, evolucion=evolucion)
    r = TendenciaTool(finanzas=mundo.finanzas).ejecutar(contexto(), TendenciaArgumentos(meses=3))
    assert r == {
        "meses": [
            {"mes": "2026-08", "gastos": "671.35", "ingresos": "2100.00"},
            {"mes": "2026-09", "gastos": "776.59", "ingresos": "2100.00"},
            {"mes": "2026-10", "gastos": "504.94", "ingresos": "2100.00"},
        ],
        "media_gastos_meses_cerrados": "723.97",
        "mes_en_curso": "2026-10 va hasta el día 29",
    }
    assert len(mundo.finanzas.consultas) == 1  # una consulta, no una por mes


def test_prevision(mundo):
    def dias(*pares):
        total, salida = Decimal(0), []
        for d, g in pares:
            total += Decimal(g)
            salida.append(GastoDelDia(d, Decimal(g), total))
        return tuple(salida)

    mundo.finanzas.resumenes[(HOGAR, OCTUBRE)] = resumen(
        OCTUBRE, por_dia=dias((date(2026, 10, 3), "338.75"), (date(2026, 10, 27), "71.40"))
    )
    mundo.finanzas.resumenes[(HOGAR, SEPTIEMBRE)] = resumen(
        SEPTIEMBRE, por_dia=dias((date(2026, 9, 5), "325.40"), (date(2026, 9, 30), "92.75"))
    )
    r = PrevisionFinDeMesTool(finanzas=mundo.finanzas).ejecutar(contexto(), SinArgumentos())
    assert r == {
        "mes": "2026-10",
        "dia": "29 de 31",
        "gastado_hasta_hoy": "410.15",
        "total_al_ritmo_actual": "438.44",
        "mes_anterior_a_estas_alturas": "325.40",
        "mes_anterior_total": "418.15",
    }
