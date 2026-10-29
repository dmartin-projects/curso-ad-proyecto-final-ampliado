# asistente/domain/services/tokens.py — cuántos tokens son, sin llamar al modelo (módulo 96)
"""Una estimación, no una cuenta: cada modelo tiene su tokenizer, y el exacto solo lo da el proveedor (Uso, en la
respuesta). Sirve para decidir ANTES de llamar si algo cabe. Por eso se equivoca hacia arriba: 3 caracteres por
token, cuando en castellano y JSON los modelos de Groq rondan los 4 (ejercicio 1: calibrarlo con los cassettes)."""

import math

CARACTERES_POR_TOKEN = 3.0


def estimar_tokens(texto: str) -> int:
    return math.ceil(len(texto) / CARACTERES_POR_TOKEN)
