# hogares/domain/exceptions/miembro_no_encontrado_exception.py (módulos 71 y 88)
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException


class MiembroNoEncontradoException(NoEncontradoException):
    mensaje = "No es miembro de este hogar."
