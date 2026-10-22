# oauth/domain/exceptions/nombre_obligatorio_exception.py (módulo 90)
from core.domain.exceptions.validacion_exception import ValidacionException


class NombreObligatorioException(ValidacionException):
    campo = "nombre"
    mensaje = "El cliente necesita un nombre: es el que verá el usuario en la pantalla de consentimiento."
