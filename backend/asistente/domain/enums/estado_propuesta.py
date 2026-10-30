# asistente/domain/enums/estado_propuesta.py — en qué punto está un cambio que propone el asistente (módulo 97)
from enum import StrEnum


class EstadoPropuesta(StrEnum):
    PENDIENTE = "pendiente"  # esperando a que la persona la confirme o la descarte
    CONFIRMADA = "confirmada"  # confirmada y hecha: el use case de la app dueña la ha ejecutado
    DESCARTADA = "descartada"
