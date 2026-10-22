# importaciones/domain/exceptions/extracto_repetido_exception.py (módulos 75 y 88)
from core.domain.exceptions.validacion_exception import ValidacionException


class ExtractoRepetidoException(ValidacionException):
    """La UniqueConstraint importacion_archivo_unico_activo: dos subidas del mismo extracto a la vez."""

    campo = "archivo"
    mensaje = "Este extracto ya se importó."
