# asistente/application/prompts/titulo.py — el título de una conversación (módulo 97)
from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt

TITULO = PlantillaDePrompt(
    nombre="titulo",
    version="2026-10-30.1",
    texto="""\
Pon título a esta conversación de una app de gastos domésticos, para una lista de conversaciones.
- Resume la pregunta de abajo: de qué trata, no lo que se responde.
- Entre 2 y 6 palabras, en el idioma de la pregunta, sin comillas ni punto final.
- Ejemplo de formato (no de tema): «¿Cuánto nos costó el seguro del coche este año?» → Coste anual del seguro del coche
Pregunta: {pregunta}""",
)
