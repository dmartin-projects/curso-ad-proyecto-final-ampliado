# tickets/domain/enums/estado_ticket.py — el ciclo de vida de un ticket (módulos 74 y 88)
#
#   pendiente ──▶ procesando ──▶ procesado
#       ▲             │   └────▶ revisar ──(confirmar)──▶ procesado
#       │             └────────▶ error
#       └──────── (reprocesar) ── revisar / error
from datetime import timedelta
from enum import StrEnum


class EstadoTicket(StrEnum):
    PENDIENTE = "pendiente"
    PROCESANDO = "procesando"
    REVISAR = "revisar"
    PROCESADO = "procesado"
    ERROR = "error"


SIN_TERMINAR = (EstadoTicket.PENDIENTE, EstadoTicket.PROCESANDO)
ATASCADO = timedelta(minutes=15)  # pendiente o procesando sin moverse: algo va mal (soporte, módulo 79; métrica, 84)
