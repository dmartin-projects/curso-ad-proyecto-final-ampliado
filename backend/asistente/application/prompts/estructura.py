# asistente/application/prompts/estructura.py — la respuesta, en JSON para la interfaz (módulo 96)
from asistente.domain.vo.plantilla_de_prompt import PlantillaDePrompt

ESTRUCTURA = PlantillaDePrompt(
    nombre="estructura",
    version="2026-10-29.1",
    texto="""\
Eres el asistente de Gastos. Acabas de contestar al usuario (tu último mensaje). Devuélvelo en el formato pedido:
- texto: tu respuesta, tal cual;
- cifras: los importes que aparecen en ella, cada uno con su concepto breve («Gasto de septiembre»);
- seguimiento: de 0 a {max_seguimiento} preguntas cortas que el usuario podría hacer a continuación sobre sus gastos, en su idioma.
No añadas datos que no estén en la conversación.""",
)
