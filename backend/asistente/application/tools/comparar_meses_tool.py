# asistente/application/tools/comparar_meses_tool.py — dos meses, categoría a categoría, en una llamada (módulo 95, ejercicio 2)
from decimal import Decimal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros
from asistente.application.tools.mes_del_contexto import MesOpcional, mes_pedido
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.exceptions.tool_exception import ToolException


class CompararMesesArgumentos(SinArgumentos):
    mes: MesOpcional = None
    # El tipo y su validación, de MesOpcional; la descripción, propia: sin 'con', el mes anterior (no el en curso)
    con: MesOpcional = Field(None, description="El mes de referencia, AAAA-MM. Si no lo envías: el anterior a 'mes'.")


class CompararMesesTool(Tool):
    nombre = "comparar_meses"
    descripcion = (
        "Compara el gasto de dos meses por categoría principal: cuánto en cada uno y la diferencia, de la que más "
        "cambia a la que menos. 'con' es el mes de referencia (sin él, el anterior a 'mes')."
    )
    Argumentos = CompararMesesArgumentos

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: CompararMesesArgumentos) -> dict:
        mes = mes_pedido(contexto, args.mes)
        con = mes_pedido(contexto, args.con) if args.con else mes.anterior()
        if con == mes:
            raise ToolException("'mes' y 'con' son el mismo mes: compara dos meses distintos.")
        a, b = (self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, m) for m in (mes, con))
        en_a = {c.categoria: c.total for c in a.por_categoria}
        en_b = {c.categoria: c.total for c in b.por_categoria}
        filas = [(n, en_a.get(n, Decimal(0)), en_b.get(n, Decimal(0))) for n in en_a | en_b]
        filas.sort(key=lambda f: abs(f[1] - f[2]), reverse=True)
        return {
            "mes": str(mes),
            "con": str(con),
            "gastos": {"mes": euros(a.gastos), "con": euros(b.gastos), "diferencia": euros(a.gastos - b.gastos)},
            "categorias": [
                {"categoria": n, "mes": euros(x), "con": euros(y), "diferencia": euros(x - y)} for n, x, y in filas
            ],
        }
