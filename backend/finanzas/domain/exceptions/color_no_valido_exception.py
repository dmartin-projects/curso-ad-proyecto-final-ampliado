# finanzas/domain/exceptions/color_no_valido_exception.py (módulo 87)
from core.domain.exceptions.validacion_exception import ValidacionException


class ColorNoValidoException(ValidacionException):
    campo = "color"
    mensaje = "El color debe tener el formato #rrggbb."
