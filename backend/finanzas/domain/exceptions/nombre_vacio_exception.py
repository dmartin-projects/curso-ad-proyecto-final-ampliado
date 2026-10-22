# finanzas/domain/exceptions/nombre_vacio_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class NombreVacioException(ValidacionException):
    campo = "nombre"
    mensaje = "El nombre no puede estar vacío."
