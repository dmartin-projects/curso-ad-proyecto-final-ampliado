# asistente/application/tools/subagente_tool.py — un subagente, visto por el orquestador como una tool (módulo 105)
from collections.abc import Callable

from pydantic import Field

from asistente.application.agent.agente import Agente
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.subagentes.subagente import Subagente
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.exceptions.tool_exception import ToolException
from asistente.domain.vo.mensaje import Mensaje

MAX_INFORME = 1500  # lo que vuelve al orquestador: un resumen, no los resultados de sus tools


class EncargoArgumentos(SinArgumentos):
    encargo: str = Field(min_length=5, max_length=400, description="Qué tiene que averiguar, con el mes: «…».")


class SubagenteTool(Tool):
    """ "Agents as tools": el orquestador llama a un especialista como llama a cualquier tool, con un encargo. El
    especialista es un Agente completo (el mismo bucle, con sus guardas), con SU prompt y SOLO sus tools, que empieza
    con el encargo y nada más: su contexto es pequeño, y lo que lee (resultados de tools, quizá de terceros) se queda en
    él. Al orquestador vuelve un resumen."""

    Argumentos = EncargoArgumentos
    max_llamadas = 2
    # Módulo 102: su informe puede llevar texto de terceros que leyó el especialista (un concepto, un comercio). Sin
    # esto, pasar por un subagente "lavaría" la procedencia
    lee_terceros = True

    def __init__(self, *, subagente: Subagente, crear_agente: Callable[[Subagente], Agente]):
        self.subagente, self.crear_agente = subagente, crear_agente
        self.nombre = f"especialista_{subagente.nombre}"
        self.descripcion = subagente.descripcion

    def ejecutar(self, contexto: ContextoPregunta, args: EncargoArgumentos) -> dict:
        r = self.crear_agente(self.subagente).responder((Mensaje.usuario(args.encargo),), contexto)
        if r.motivo != MotivoParada.FIN:
            raise ToolException(f"El especialista {self.subagente.nombre} no ha terminado ({r.motivo}): sigue sin él.")
        return {
            "especialista": self.subagente.nombre,
            "informe": r.texto[:MAX_INFORME],
            "tools": [ll.nombre for ll in r.llamadas],
        }
