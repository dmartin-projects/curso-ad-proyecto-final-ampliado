# tickets/domain/exceptions/ticket_repetido_exception.py (módulos 74 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class TicketRepetidoException(ValidacionException):
    """La UniqueConstraint ticket_archivo_unico_por_hogar: dos subidas del mismo archivo a la vez."""

    campo = "archivo"
    mensaje = "Este ticket ya se subió."
