# asistente/application/tools/listar_miembros_tool.py — quiénes forman parte del hogar (módulo 97)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_membresias import IMembresias
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool


class ListarMiembrosTool(Tool):
    nombre = "listar_miembros"
    descripcion = "Quiénes forman parte del hogar y con qué rol (admin, miembro o lector)."
    max_llamadas = 1  # no cambian durante una pregunta

    def __init__(self, *, membresias: IMembresias):
        self.membresias = membresias

    def ejecutar(self, contexto: ContextoPregunta, args: SinArgumentos) -> dict:
        # Solo el nombre y el rol: ni emails ni ids (lo que no viaja no se puede filtrar, módulo 102)
        miembros = self.membresias.miembros(contexto.actor, contexto.hogar.id)
        return {"miembros": [{"nombre": m.nombre, "rol": m.rol} for m in miembros]}
