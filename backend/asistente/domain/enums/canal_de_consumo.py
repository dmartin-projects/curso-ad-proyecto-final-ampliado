# asistente/domain/enums/canal_de_consumo.py — para qué se llamó al modelo (módulo 98)
from enum import StrEnum


class CanalDeConsumo(StrEnum):
    """Lo que se paga no es solo la respuesta: también lo que el usuario no ve. Separado, se ve qué cuesta cada cosa."""

    CHAT = "chat"  # la respuesta: el agent loop y la llamada que la estructura
    TITULO = "titulo"  # el título de una conversación nueva, con el modelo auxiliar
    RESUMEN = "resumen"  # módulo 99: resumir lo antiguo de una conversación larga, con el modelo auxiliar
    AYUDA = "ayuda"  # ejercicio 1 del 100: reescribir y reordenar la búsqueda en la ayuda, con el modelo auxiliar
    ANALISIS = "analisis"  # módulo 105: el análisis del mes (el orquestador y sus especialistas), en Celery
