# finanzas/domain/enums/origen.py — de dónde viene un movimiento (módulos 72 y 87)
from enum import StrEnum


class Origen(StrEnum):
    MANUAL = "manual"
    TICKET = "ticket"
    EXTRACTO = "extracto"
