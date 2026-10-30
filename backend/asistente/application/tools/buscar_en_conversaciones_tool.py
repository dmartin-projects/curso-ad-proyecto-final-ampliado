# asistente/application/tools/buscar_en_conversaciones_tool.py — la memoria de las conversaciones (módulo 105)
"""La memoria a largo plazo de la persona, la que no ha pedido guardar: lo que se dijo en SUS conversaciones
anteriores ("¿qué te conté del viaje a Londres?"). Distinta de los recuerdos (módulo 99), que viajan siempre y son
pocos: esta se consulta solo cuando hace falta, y no ocupa contexto si no.

Privacidad: solo las conversaciones de quien pregunta en este hogar (ni las de otros miembros), solo lo visible (ni
resultados de tools ni adjuntos), la conversación actual fuera, y nada que no esté ya en la app: borrar una
conversación la borra también de esta memoria.
"""

from pydantic import Field

from asistente.application.agent.contexto_pregunta import ContextoPregunta
from asistente.application.tools.sin_argumentos import SinArgumentos
from asistente.application.tools.tool import Tool
from asistente.domain.repositories.i_conversacion_query_service import IConversacionQueryService
from asistente.domain.services.normalizar import sin_tildes

MAX_CONVERSACIONES, CONTEXTO = 3, 160


class BuscarEnConversacionesArgumentos(SinArgumentos):
    texto: str = Field(min_length=3, max_length=60, description="Una palabra o expresión: «Londres», «hipoteca».")


class BuscarEnConversacionesTool(Tool):
    nombre = "buscar_en_conversaciones"
    descripcion = (
        "Busca en las conversaciones ANTERIORES de esta persona contigo (no en los datos de la app). Úsala cuando se "
        "refiera a algo que hablasteis otro día («lo que te dije del viaje»)."
    )
    Argumentos = BuscarEnConversacionesArgumentos
    lee_terceros = True  # lo que dijo el modelo otro día pudo salir de un ticket o de un extracto (módulo 102)
    max_llamadas = 2

    def __init__(self, *, consultas: IConversacionQueryService):
        self.consultas = consultas

    def ejecutar(self, contexto: ContextoPregunta, args: BuscarEnConversacionesArgumentos) -> dict:
        encontradas = [
            c
            for c in self.consultas.listar(contexto.usuario_id, contexto.hogar.id, limite=10, busqueda=args.texto)
            if c.id != contexto.conversacion_id
        ][:MAX_CONVERSACIONES]
        aguja = sin_tildes(args.texto.lower())
        resultados = []
        for c in encontradas:
            detalle = self.consultas.detalle(contexto.usuario_id, contexto.hogar.id, c.id)
            fragmentos = [_fragmento(m.texto, aguja) for m in detalle.mensajes if aguja in sin_tildes(m.texto.lower())]
            resultados.append({"titulo": c.titulo, "fecha": str(c.actualizada.date()), "dice": fragmentos[:2]})
        if not resultados:
            return {"encontradas": 0, "nota": "No habéis hablado de eso en otras conversaciones."}
        return {"encontradas": len(resultados), "conversaciones": resultados}


def _fragmento(texto: str, aguja: str) -> str:
    plano = " ".join(texto.split())
    i = max(0, sin_tildes(plano.lower()).find(aguja) - CONTEXTO // 2)
    return ("…" if i else "") + plano[i : i + CONTEXTO] + ("…" if i + CONTEXTO < len(plano) else "")
