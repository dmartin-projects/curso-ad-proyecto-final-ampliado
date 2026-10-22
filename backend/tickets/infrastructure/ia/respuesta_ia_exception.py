# tickets/infrastructure/ia/respuesta_ia_exception.py (módulos 74 y 88)
from tickets.infrastructure.ia.ia_exception import IAException


class RespuestaIAException(IAException):
    """La IA respondió, pero algo no cuadra (JSON inválido, datos imposibles, 4xx): reintentar no ayuda."""
