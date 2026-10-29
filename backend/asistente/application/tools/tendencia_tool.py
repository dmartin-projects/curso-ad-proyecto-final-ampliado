# asistente/application/tools/tendencia_tool.py — la evolución de los últimos meses, de una vez (módulo 95)
from decimal import Decimal

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from core.domain.vo.mes import Mes


class TendenciaArgumentos(SinArgumentos):
    meses: int = Field(6, ge=2, le=12, description="Cuántos meses, contando el actual (de 2 a 12).")


class TendenciaTool(Tool):
    nombre = "tendencia"
    descripcion = (
        "Gastos e ingresos de cada uno de los últimos meses, en una sola llamada. Para '¿cómo hemos ido este año?' o "
        "'¿estamos gastando más?': no llames a resumen_mes mes a mes."
    )
    Argumentos = TendenciaArgumentos

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: TendenciaArgumentos) -> dict:
        actual = Mes.de(contexto.hoy)
        r = self.finanzas.resumen_del_mes(contexto.actor, contexto.hogar.id, actual)
        meses = [m for m in r.evolucion if m.mes in actual.ultimos(args.meses)]
        cerrados = [m.gastos for m in meses if m.mes != actual]
        return {
            "meses": [{"mes": str(m.mes), "gastos": euros(m.gastos), "ingresos": euros(m.ingresos)} for m in meses],
            "media_gastos_meses_cerrados": euros(sum(cerrados, Decimal(0)) / len(cerrados)) if cerrados else None,
            "mes_en_curso": f"{actual} va hasta el día {contexto.hoy.day}",
        }
