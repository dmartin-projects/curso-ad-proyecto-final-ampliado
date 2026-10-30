# asistente/application/tools/buscar_movimientos_tool.py — buscar movimientos, con el total y la suma de TODOS (módulo 95)
from typing import Literal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.categoria_por_nombre import categoria_por_nombre
from asistente.application.tools.formato import corto, euros
from asistente.application.tools.periodo import FechaOpcional, periodo
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.vo.filtro_de_movimientos import FiltroDeMovimientos


class BuscarMovimientosArgumentos(SinArgumentos):
    texto: str | None = Field(None, max_length=60, description="En el concepto, el comercio o las notas.")
    categoria: str | None = Field(
        None, max_length=60, description="Una categoría, como la dice el usuario (incluye sus subcategorías)."
    )
    desde: FechaOpcional = None
    hasta: FechaOpcional = None
    tipo: Literal["gasto", "ingreso"] | None = Field(None, description="Solo gastos o solo ingresos.")
    limite: int = Field(10, ge=1, le=20, description="Cuántos movimientos de ejemplo.")


class BuscarMovimientosTool(Tool):
    nombre = "buscar_movimientos"
    descripcion = (
        "Busca movimientos por texto, categoría, fechas o tipo. Devuelve el número y la suma de TODOS los que cumplen "
        "el filtro y los más recientes como ejemplo: para '¿cuánto en Mercadona este año?' usa la suma, sin paginar. "
        "Sin fechas: el mes en curso."
    )
    Argumentos = BuscarMovimientosArgumentos
    lee_terceros = True  # módulo 102: conceptos de extractos bancarios (los escribe quien hace la transferencia)

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: BuscarMovimientosArgumentos) -> dict:
        desde, hasta = periodo(contexto, args.desde, args.hasta)
        categoria = categoria_por_nombre(self.finanzas, contexto, args.categoria) if args.categoria else None
        filtro = FiltroDeMovimientos(desde, hasta, args.texto, categoria.id if categoria else None, args.tipo)
        r = self.finanzas.movimientos(contexto.actor, contexto.hogar.id, filtro, args.limite)
        return {
            "periodo": f"{desde} a {hasta}",
            "total": r.total,
            "suma_gastos": euros(r.gastos),
            "suma_ingresos": euros(r.ingresos),
            "movimientos": [
                {
                    "fecha": str(m.fecha),
                    "importe": euros(m.importe),
                    "concepto": corto(m.concepto),
                    **({"categoria": m.categoria} if m.categoria else {}),
                    **({"comercio": m.comercio} if m.comercio else {}),
                }
                for m in r.primeros
            ],
            **({"sin_mostrar": r.total - len(r.primeros)} if r.total > len(r.primeros) else {}),
        }
