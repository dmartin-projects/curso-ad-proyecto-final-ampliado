# asistente/domain/enums/esfuerzo_de_razonamiento.py — cuánto "piensa" el modelo antes de contestar (módulo 93)
from enum import StrEnum


class EsfuerzoDeRazonamiento(StrEnum):
    """Los modelos de razonamiento generan tokens ocultos antes de la respuesta. Se pagan como salida y tardan.

    Nombres propios: el adapter los traduce (reasoning_effort low/medium/high en Groq y OpenAI; thinking_level en
    Gemini; budget_tokens en Claude). Un modelo que no razona los ignora o devuelve un error de petición.
    """

    BAJO = "bajo"
    MEDIO = "medio"
    ALTO = "alto"
