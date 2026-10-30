# asistente/domain/enums/canal_de_consumo.py — para qué se llamó al modelo (módulo 98)
from enum import StrEnum


class CanalDeConsumo(StrEnum):
    """Lo que se paga no es solo la respuesta: también lo que el usuario no ve. Separado, se ve qué cuesta cada cosa."""

    CHAT = "chat"  # la respuesta: el agent loop y la llamada que la estructura
    TITULO = "titulo"  # el título de una conversación nueva, con el modelo auxiliar
