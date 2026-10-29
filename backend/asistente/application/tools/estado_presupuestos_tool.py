# asistente/application/tools/estado_presupuestos_tool.py — cómo van los presupuestos de un mes (módulo 95)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros
from asistente.application.tools.mes_del_contexto import MesOpcional, mes_pedido
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool

AVISO = 80  # % a partir del cual un presupuesto está "cerca" (el mismo umbral que los avisos del módulo 76)


class EstadoPresupuestosArgumentos(SinArgumentos):
    mes: MesOpcional = None


class EstadoPresupuestosTool(Tool):
    nombre = "estado_presupuestos"
    descripcion = "Los presupuestos de un mes por categoría: límite, gastado, porcentaje y si está superado."
    Argumentos = EstadoPresupuestosArgumentos

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: EstadoPresupuestosArgumentos) -> dict:
        mes = mes_pedido(contexto, args.mes)
        r = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, mes)
        if not r.presupuestos:  # que diga "no hay", no que los invente
            return {"mes": str(mes), "presupuestos": [], "nota": f"El hogar no tiene presupuestos en {mes}."}
        resultado = {
            "mes": str(mes),
            "presupuestos": [
                {
                    "categoria": p.categoria,
                    "limite": euros(p.importe),
                    "gastado": euros(p.gastado),
                    "porcentaje": p.porcentaje,
                    "estado": "superado" if p.porcentaje > 100 else "cerca" if p.porcentaje >= AVISO else "bien",
                }
                for p in r.presupuestos
            ],
        }
        if mes.contiene(contexto.hoy):
            resultado["mes_en_curso"] = f"hasta el día {contexto.hoy.day}"
        return resultado
