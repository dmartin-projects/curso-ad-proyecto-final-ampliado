# importaciones/domain/enums/accion.py — qué se hace con cada fila (módulos 75 y 88)
from enum import StrEnum


class Accion(StrEnum):
    """Qué se hace con una fila del extracto."""

    CREAR = "crear"
    DUPLICADA = "duplicada"
    CONCILIAR = "conciliar"
