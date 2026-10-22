# hogares/domain/exceptions/hogar_no_encontrado_exception.py (módulos 71 y 88)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class HogarNoEncontradoException(NoEncontradoException):
    mensaje = "El hogar no existe."
