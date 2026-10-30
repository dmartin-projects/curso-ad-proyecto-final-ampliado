# asistente/application/tools/listar_cuentas_tool.py — las cuentas del hogar, con su saldo (módulo 97)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.formato import euros
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool


class ListarCuentasTool(Tool):
    nombre = "listar_cuentas"
    descripcion = (
        "Las cuentas del hogar (banco, efectivo, tarjeta…) con su saldo de hoy. Para '¿cuánto tenemos en la cuenta "
        "común?' o para saber en qué cuenta apuntar algo."
    )
    max_llamadas = 1

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: SinArgumentos) -> dict:
        return {
            "cuentas": [
                {"nombre": c.nombre, "tipo": c.tipo, "saldo": euros(c.saldo), **({} if c.activa else {"activa": False})}
                for c in self.finanzas.cuentas(contexto.actor, contexto.hogar.id)
            ]
        }
