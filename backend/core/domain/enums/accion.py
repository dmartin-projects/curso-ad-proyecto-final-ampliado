# core/domain/enums/accion.py — lo que se apunta en la auditoría (módulos 17 y 87)
from enum import StrEnum


class Accion(StrEnum):
    CREAR = "crear"
    MODIFICAR = "modificar"
    BORRAR = "borrar"
