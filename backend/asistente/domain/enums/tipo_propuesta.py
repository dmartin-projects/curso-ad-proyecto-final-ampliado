# asistente/domain/enums/tipo_propuesta.py — los cambios que el asistente sabe proponer (módulo 97)
from enum import StrEnum


class TipoPropuesta(StrEnum):
    MOVIMIENTO = "movimiento"  # apuntar un gasto o un ingreso (RegistrarMovimientoUseCase de finanzas)
