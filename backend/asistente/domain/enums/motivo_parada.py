# asistente/domain/enums/motivo_parada.py — por qué ha terminado el agente una pregunta (módulo 94)
from enum import StrEnum


class MotivoParada(StrEnum):
    FIN = "fin"  # el modelo ha contestado
    LIMITE_ITERACIONES = "limite_iteraciones"  # MAX_ITERATIONS: ni en la última vuelta (sin tools) ha contestado
    RESPUESTA_CORTADA = "respuesta_cortada"  # el texto llega a medias (max_tokens)
    BLOQUEADA = "bloqueada"  # los filtros del proveedor
