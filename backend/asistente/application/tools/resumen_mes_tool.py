# asistente/application/tools/resumen_mes_tool.py — los totales de un mes (módulo 94)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros, pct
from asistente.application.tools.mes_del_contexto import MesOpcional, mes_pedido
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool


class ResumenMesArgumentos(SinArgumentos):
    mes: MesOpcional = None


class ResumenMesTool(Tool):
    nombre = "resumen_mes"
    descripcion = (
        "Totales de un mes del hogar: gastos, ingresos, balance, número de movimientos y variación del gasto frente al "
        "mes anterior. Para '¿cuánto gastamos en septiembre?' o '¿cómo vamos este mes?'. El desglose por categoría "
        "está en gasto_por_categoria."
    )
    Argumentos = ResumenMesArgumentos

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: ResumenMesArgumentos) -> dict:
        mes = mes_pedido(contexto, args.mes)
        r = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, mes)
        resultado = {
            "mes": str(r.mes),
            "gastos": euros(r.gastos),
            "ingresos": euros(r.ingresos),
            "balance": euros(r.balance),
            "movimientos": r.num_movimientos,
            "gastos_mes_anterior": euros(r.gastos_mes_anterior),
            "variacion_gastos_pct": pct(r.variacion),
        }
        if mes.contiene(contexto.hoy):  # el modelo tiene que saber que el mes no ha terminado: no es un mes "bajo"
            resultado["mes_en_curso"] = f"hasta el día {contexto.hoy.day}"
        if r.pendientes_revision:
            resultado["movimientos_sin_revisar"] = r.pendientes_revision
        return resultado
