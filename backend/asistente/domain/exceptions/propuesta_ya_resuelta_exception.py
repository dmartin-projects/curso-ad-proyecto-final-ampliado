# asistente/domain/exceptions/propuesta_ya_resuelta_exception.py (módulo 97)
from core.domain.exceptions.dominio_exception import DominioException


class PropuestaYaResueltaException(DominioException):
    """Confirmada, descartada o caducada: un 409, como cualquier cambio sobre un estado que ya no es el que se vio."""

    codigo = "propuesta_ya_resuelta"
    mensaje = "Esta propuesta ya no está pendiente."
