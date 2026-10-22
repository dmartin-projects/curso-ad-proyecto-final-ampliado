# oauth/domain/exceptions/aplicacion_no_conectada_exception.py (ejercicio 1 del módulo 90)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class AplicacionNoConectadaException(NoEncontradoException):
    """Ejercicio 1: el usuario no tiene ningún acceso activo dado a esa aplicación (o no existe)."""

    mensaje = "Esa aplicación no tiene acceso a tu cuenta."
