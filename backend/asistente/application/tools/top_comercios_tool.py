# asistente/application/tools/top_comercios_tool.py — dónde se gasta más (módulo 95)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros
from asistente.application.tools.mes_del_contexto import MesOpcional, mes_pedido
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool


class TopComerciosArgumentos(SinArgumentos):
    mes: MesOpcional = None


class TopComerciosTool(Tool):
    nombre = "top_comercios"
    descripcion = "Los 5 comercios con más gasto de un mes, con cuántas veces se compró en cada uno."
    Argumentos = TopComerciosArgumentos
    lee_terceros = True  # módulo 102: nombres de comercio leídos de tickets y extractos

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: TopComerciosArgumentos) -> dict:
        mes = mes_pedido(contexto, args.mes)
        r = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, mes)
        return {
            "mes": str(mes),
            "comercios": [{"comercio": c.comercio, "total": euros(c.total), "veces": c.veces} for c in r.top_comercios],
        }
