# asistente/application/prompts/memoria.py — lo que el asistente sabe de antes, como contexto (módulo 99)
"""Dos bloques que viajan al principio de la conversación (después del system prompt y las tools), en un mensaje de
contexto: lo que la persona pidió recordar (todas sus conversaciones) y el resumen de lo antiguo de ESTA conversación.

No van en el system prompt: así el system prompt sigue siendo el mismo para todas las conversaciones de un día (el
golden file, las versiones), y el prefijo que el proveedor cachea (instrucciones + tools) no cambia de una persona a
otra del mismo hogar. Son prompts como los demás: con versión y huella."""

from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt

RECUERDOS = PlantillaDePrompt(
    nombre="recuerdos",
    version="2026-10-30.1",
    texto="""\
<recuerdos>
{recuerdos}
</recuerdos>
Esto te pidió la persona que recordaras. Tenlo en cuenta en tus respuestas; si contradice lo que dice ahora, manda \
lo de ahora.""",
)

RESUMEN_PREVIO = PlantillaDePrompt(
    nombre="resumen_previo",
    version="2026-10-30.1",
    texto="""\
<resumen_de_la_conversacion>
{resumen}
</resumen_de_la_conversacion>
Es lo que hablasteis antes en esta conversación, resumido. Lo que sigue es lo más reciente. Si te preguntan por algo \
de antes que el resumen no detalla, vuelve a consultar los datos con las tools.""",
)

RESUMIR = PlantillaDePrompt(
    nombre="resumir",
    version="2026-10-30.1",
    texto="""\
Resume esta conversación entre una persona y el asistente de gastos de su hogar, para que el asistente pueda seguirla \
sin leerla entera.
- Conserva qué se preguntó y las cifras, meses, categorías y comercios de las respuestas, exactos.
- Conserva lo que la persona contó de sí misma o del hogar.
- Nada que no esté en la conversación. Sin saludos ni valoraciones.
- Como mucho {palabras} palabras, en frases cortas: «Preguntó por…; el asistente contestó…».
{anterior}<conversacion>
{conversacion}
</conversacion>""",
)
