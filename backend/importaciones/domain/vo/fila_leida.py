# importaciones/domain/vo/fila_leida.py — una fila leída de un extracto, sea del banco que sea (módulos 75 y 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class FilaLeida:
    numero: int  # línea del archivo (para los mensajes)
    fecha: date
    concepto: str
    importe: Decimal
    saldo: Decimal | None = None
