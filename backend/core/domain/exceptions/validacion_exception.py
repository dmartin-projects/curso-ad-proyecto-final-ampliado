# core/domain/exceptions/validacion_exception.py (módulo 87)
from core.domain.exceptions.dominio_exception import DominioException


class ValidacionException(DominioException):
    """Un dato no cumple una regla del dominio (importe cero, color que no es un color…)."""

    codigo = "validacion"
    status = 400
    mensaje = "Los datos enviados no son válidos."
