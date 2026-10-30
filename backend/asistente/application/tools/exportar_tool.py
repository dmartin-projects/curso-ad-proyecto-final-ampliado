# asistente/application/tools/exportar_tool.py — un CSV para descargar, sin pasar las filas por el modelo (módulo 97)
from typing import Literal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.ports.i_exportador_de_movimientos import IExportadorDeMovimientos
from asistente.application.tools.categoria_por_nombre import categoria_por_nombre
from asistente.application.tools.con_artefacto import ConArtefacto
from asistente.application.tools.periodo import FechaOpcional, periodo
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos


class ExportarArgumentos(SinArgumentos):
    texto: str | None = Field(None, max_length=60, description="En el concepto, el comercio o las notas.")
    categoria: str | None = Field(None, max_length=60, description="Una categoría, como la dice el usuario.")
    desde: FechaOpcional = None
    hasta: FechaOpcional = None
    tipo: Literal["gasto", "ingreso"] | None = Field(None, description="Solo gastos o solo ingresos.")


class ExportarTool(Tool):
    nombre = "exportar"
    descripcion = (
        "Prepara un CSV con los movimientos de un filtro (texto, categoría, fechas, tipo) para descargarlo: para "
        "'pásamelo a Excel' o 'descárgame los gastos de septiembre'. Sin fechas: el mes en curso. La interfaz enseña "
        "el enlace; tú no escribas ninguno."
    )
    Argumentos = ExportarArgumentos
    max_llamadas = 1

    def __init__(self, *, finanzas: IConsultasDeFinanzas, exportador: IExportadorDeMovimientos):
        self.finanzas = finanzas
        self.exportador = exportador

    def ejecutar(self, contexto: ContextoPregunta, args: ExportarArgumentos) -> dict | ConArtefacto:
        desde, hasta = periodo(contexto, args.desde, args.hasta)
        categoria = categoria_por_nombre(self.finanzas, contexto, args.categoria) if args.categoria else None
        filtro = FiltroDeMovimientos(desde, hasta, args.texto, categoria.id if categoria else None, args.tipo)
        archivo = self.exportador.exportar(
            contexto.actor, contexto.hogar.id, filtro, f"movimientos-{desde}-{hasta}.csv"
        )
        if not archivo.filas:  # sin filas no hay archivo: que el modelo lo diga, no que ofrezca un CSV vacío
            return {"filas": 0, "nota": "No hay movimientos con ese filtro: no se ha preparado ningún archivo."}
        return ConArtefacto(
            {"archivo": archivo.nombre, "filas": archivo.filas, "nota": "Listo: la interfaz enseña el enlace."},
            archivo,
        )
