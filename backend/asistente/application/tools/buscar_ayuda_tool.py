# asistente/application/tools/buscar_ayuda_tool.py — "¿cómo se hace…?": la ayuda de la app (módulo 100)
from pydantic import BaseModel, ConfigDict, Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.ayuda.buscador_de_ayuda import BuscadorDeAyuda
from asistente.application.tools.tool import Tool


class BuscarAyudaArgumentos(BaseModel):
    model_config = ConfigDict(extra="forbid")
    pregunta: str = Field(
        min_length=3, max_length=300, description="La duda sobre la app, con las palabras de la persona."
    )


class BuscarAyudaTool(Tool):
    """La G de RAG la hace el agente de siempre: esta tool solo trae los pasajes, y el modelo contesta con ellos (y los
    cita). Solo en el chat: es ayuda de la INTERFAZ ("pulsa Generar en Informes"), que en la terminal no tiene sentido."""

    nombre = "buscar_ayuda"
    descripcion = (
        "Busca en la ayuda de la app cómo se hace algo en Gastos (importar un extracto, invitar a alguien, la "
        "verificación en dos pasos…). Para dudas sobre la app, no sobre los datos del hogar. Contesta con lo que diga "
        "y cita la sección."
    )
    Argumentos = BuscarAyudaArgumentos
    max_llamadas = 2

    def __init__(self, *, buscador: BuscadorDeAyuda):
        self.buscador = buscador

    def ejecutar(self, contexto: ContextoPregunta, args: BuscarAyudaArgumentos) -> dict:
        r = self.buscador.buscar(args.pregunta)
        if not r.pasajes:
            return {"pasajes": [], "nota": "La ayuda no dice nada de esto: dilo así, no lo inventes."}
        return {
            "pasajes": [{"fuente": p.fuente, "titulo": p.titulo, "texto": p.texto} for p in r.pasajes],
            "nota": "Contesta solo con lo que dicen estos pasajes y cita la sección (p. ej. «según la ayuda, Tickets»).",
        }
