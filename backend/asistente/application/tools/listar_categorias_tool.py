# asistente/application/tools/listar_categorias_tool.py — las categorías del hogar, con su principal (módulo 95)
from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ports.i_consultas_de_finanzas import IConsultasDeFinanzas
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool


class ListarCategoriasTool(Tool):
    nombre = "listar_categorias"
    descripcion = (
        "Las categorías del hogar, con su categoría principal. Para '¿qué categorías tenemos?' o para saber qué nombre "
        "usar si el que dice el usuario no está."
    )
    max_llamadas = 1  # no cambian durante una pregunta

    def __init__(self, *, finanzas: IConsultasDeFinanzas):
        self.finanzas = finanzas

    def ejecutar(self, contexto: ContextoPregunta, args: SinArgumentos) -> dict:
        return {
            "categorias": [
                {
                    "nombre": c.nombre,
                    **({"dentro_de": c.padre} if c.padre else {}),
                    **({"ingreso": True} if c.es_ingreso else {}),
                }
                for c in self.finanzas.categorias(contexto.actor, contexto.hogar.id)
            ]
        }
