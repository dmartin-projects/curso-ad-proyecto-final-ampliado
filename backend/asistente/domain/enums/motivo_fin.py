# asistente/domain/enums/motivo_fin.py — por qué ha dejado de generar el modelo (módulo 93)
from enum import StrEnum


class MotivoFin(StrEnum):
    """El finish_reason de cada proveedor, en un idioma propio: es lo que el agent loop (módulo 94) mira."""

    FIN = "fin"  # ha terminado de hablar
    TOOLS = "tools"  # pide tool calls y espera sus resultados
    LIMITE_TOKENS = "limite_tokens"  # cortado por max_tokens: la respuesta está incompleta (un JSON, roto)
    BLOQUEADA = "bloqueada"  # los filtros de contenido del proveedor
    OTRO = "otro"
