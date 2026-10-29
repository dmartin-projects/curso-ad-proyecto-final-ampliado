# asistente/domain/vo/llamada_tool.py — el modelo PIDE ejecutar una función (módulo 93)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LlamadaTool:
    """Un tool call. El modelo no ejecuta nada: devuelve el nombre y los argumentos, y la ejecuta nuestro código.

    `argumentos` es el JSON TAL CUAL lo escribió el modelo: puede no ser JSON válido, o no cumplir el schema. Se
    valida al ejecutar la tool (módulo 94), igual que el body de una request.
    """

    id: str  # para emparejar la llamada con su resultado
    nombre: str
    argumentos: str = "{}"
