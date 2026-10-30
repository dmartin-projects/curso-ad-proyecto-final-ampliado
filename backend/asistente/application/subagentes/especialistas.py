# asistente/application/subagentes/especialistas.py — los tres especialistas del análisis del mes (módulo 105)
from asistente.application.prompts.subagentes import COMERCIOS, GASTOS, PRESUPUESTOS
from asistente.application.subagentes.subagente import Subagente

ESPECIALISTAS = (
    Subagente(
        "gastos",
        "El gasto del mes: total, categorías y comparación con meses anteriores.",
        GASTOS,
        ("resumen_mes", "gasto_por_categoria", "comparar_meses", "tendencia"),
    ),
    Subagente(
        "presupuestos",
        "Los presupuestos del mes y la previsión de cómo acabará.",
        PRESUPUESTOS,
        ("estado_presupuestos", "prevision_fin_de_mes"),
    ),
    Subagente(
        "comercios",
        "Dónde se gasta: los comercios, los movimientos que llaman la atención y los pagos que se repiten.",
        COMERCIOS,
        ("top_comercios", "buscar_movimientos"),
    ),
)
