# asistente/domain/vo/resultado_tool.py — lo que se devuelve al modelo por cada LlamadaTool (módulo 93)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ResultadoTool:
    llamada_id: str  # el id de la LlamadaTool que responde
    nombre: str
    contenido: str  # texto (normalmente JSON): el modelo lo lee como lee cualquier otro mensaje
    es_error: bool = False  # un error también es un resultado: el modelo lo lee y se corrige (módulo 94)
