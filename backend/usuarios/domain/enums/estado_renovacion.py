# usuarios/domain/enums/estado_renovacion.py — qué pasa al renovar una sesión (módulo 92)
from enum import StrEnum


class EstadoRenovacion(StrEnum):
    ROTADA = "rotada"  # era el vigente: se rota
    CONCURRENTE = "concurrente"  # el anterior, recién rotado por otra pestaña: un access, sin rotar
    REUTILIZADA = "reutilizada"  # uno ya rotado, fuera de ese margen: lo tiene alguien más
    CERRADA = "cerrada"  # la sesión está cerrada, ha caducado o no existe
