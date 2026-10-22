# estadisticas/domain/enums/topic.py (módulo 89)
from enum import StrEnum


class Topic(StrEnum):
    """Qué cuenta cada topic de Kafka. Los nombres reales ("gastos.movimientos"…) son configuración: el dominio
    no los conoce, y en los tests se usan topics de usar y tirar."""

    MOVIMIENTOS = "movimientos"
    MEMBRESIAS = "membresias"
