# tickets/domain/exceptions/ticket_no_encontrado_exception.py (módulos 74 y 88)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class TicketNoEncontradoException(NoEncontradoException):
    mensaje = "El ticket no existe."
