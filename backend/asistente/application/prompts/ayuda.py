# asistente/application/prompts/ayuda.py — los prompts de la búsqueda en la ayuda (módulo 100)
from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt

# La pregunta del chat no es una buena búsqueda: "¿y eso cómo lo quito?" no tiene ni una palabra de la ayuda. El
# modelo pequeño la reescribe con las palabras con que la ayuda habla de la app
REESCRIBIR = PlantillaDePrompt(
    nombre="reescribir_busqueda",
    version="2026-10-30.1",
    texto="""\
Convierte la pregunta de una persona sobre la app de gastos domésticos Gastos en una búsqueda para su ayuda.
- Usa las palabras con que la ayuda habla de la app: movimiento, gasto, ingreso, cuenta, categoría, ticket, extracto, \
importar, presupuesto, informe, hogar, miembro, rol, invitación, verificación en dos pasos, passkey, sesión, asistente.
- Entre 3 y 10 palabras, sin signos ni explicaciones. Solo la búsqueda, en una línea.
Pregunta: {pregunta}""",
)

# El reranking: de los candidatos que dan las búsquedas, cuáles contestan de verdad la pregunta, en orden
ORDENAR = PlantillaDePrompt(
    nombre="ordenar_pasajes",
    version="2026-10-30.1",
    texto="""\
Pregunta de una persona sobre la app Gastos: {pregunta}

Pasajes de la ayuda de la app:
{pasajes}

¿Qué pasajes ayudan a contestar la pregunta? Devuelve sus números, del que mejor la contesta al que menos, como mucho \
{maximo}. Si ninguno la contesta, una lista vacía.""",
)
