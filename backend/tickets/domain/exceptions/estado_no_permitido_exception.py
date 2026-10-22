# tickets/domain/exceptions/estado_no_permitido_exception.py (módulos 74 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class EstadoNoPermitidoException(DominioException):
    codigo = "ticket_estado_no_permitido"
    mensaje = "El ticket no está en un estado que permita esta operación."
