# asistente/application/prompts/comparar.py — el juez que compara dos respuestas (ejercicio 3 del 103)
from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt

COMPARAR = PlantillaDePrompt(
    nombre="comparar",
    version="2026-10-30.1",
    texto="""\
Comparas dos respuestas del asistente de una app de gastos domésticos a la misma pregunta, según una rúbrica.
Decide cuál la cumple mejor: "A", "B" o "empate" si las dos la cumplen igual (o igual de mal).
- La longitud no es calidad. El orden en que aparecen no importa.
- Escribe primero tu razonamiento (dos o tres frases) y después la decisión.""",
)
