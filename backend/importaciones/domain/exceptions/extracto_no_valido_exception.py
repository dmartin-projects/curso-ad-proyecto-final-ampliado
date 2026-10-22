# importaciones/domain/exceptions/extracto_no_valido_exception.py (módulos 75 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class ExtractoNoValidoException(DominioException):
    """El archivo no se puede leer como un extracto. Lo lanza el adapter del lector; la importación acaba en error."""

    codigo = "extracto_no_valido"
    mensaje = "El archivo no es un extracto que se pueda leer."
