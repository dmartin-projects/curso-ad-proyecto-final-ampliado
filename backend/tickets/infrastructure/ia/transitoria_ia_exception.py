# tickets/infrastructure/ia/transitoria_ia_exception.py (módulos 74 y 88)
from tickets.infrastructure.ia.ia_exception import IAException


class TransitoriaIAException(IAException):
    """Timeout, 429, 5xx, red: tiene sentido reintentar más tarde."""
