# asistente/application/tools/gasto_por_categoria_tool.py — en qué se fue el dinero de un mes (módulo 94)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros, pct
from asistente.application.tools.mes_del_contexto import MesOpcional, mes_pedido
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool


class GastoPorCategoriaArgumentos(SinArgumentos):
    mes: MesOpcional = None


class GastoPorCategoriaTool(Tool):
    nombre = "gasto_por_categoria"
    descripcion = (
        "Gasto de un mes del hogar por categoría principal (las subcategorías suman en su principal), de mayor a menor, "
        "con su porcentaje. Para '¿en qué gastamos más en agosto?' o '¿cuánto se fue en supermercado?'. Para comparar "
        "dos meses, llámala una vez por mes."
    )
    Argumentos = GastoPorCategoriaArgumentos

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: GastoPorCategoriaArgumentos) -> dict:
        mes = mes_pedido(contexto, args.mes)
        r = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, mes)
        return {
            "mes": str(mes),
            "gastos": euros(r.gastos),
            "categorias": [
                {"categoria": c.categoria, "total": euros(c.total), "porcentaje": pct(c.porcentaje)}
                for c in r.por_categoria
            ],
        }
