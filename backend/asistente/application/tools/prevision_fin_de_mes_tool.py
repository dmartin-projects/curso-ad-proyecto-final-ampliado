# asistente/application/tools/prevision_fin_de_mes_tool.py — ¿cuánto llevaremos a fin de mes? (módulo 95)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.services.prevision import prever
from core.domain.vo.mes import Mes


class PrevisionFinDeMesTool(Tool):
    nombre = "prevision_fin_de_mes"
    descripcion = (
        "Previsión del gasto del mes en curso: lo gastado hasta hoy, el total al ritmo actual y lo que llevabais el "
        "mismo día del mes anterior. Es una estimación: dilo así."
    )

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: SinArgumentos) -> dict:
        actual = Mes.de(contexto.hoy)
        este = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, actual)
        anterior = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, actual.anterior())
        p = prever(contexto.hoy, este.por_dia, anterior.por_dia or None)
        resultado = {
            "mes": str(actual),
            "dia": f"{p.dias_transcurridos} de {p.dias_del_mes}",
            "gastado_hasta_hoy": euros(p.gastado),
            "total_al_ritmo_actual": euros(p.al_ritmo_actual),
        }
        if p.mes_anterior_total is not None:
            resultado["mes_anterior_a_estas_alturas"] = euros(p.mes_anterior_a_estas_alturas)
            resultado["mes_anterior_total"] = euros(p.mes_anterior_total)
        return resultado
