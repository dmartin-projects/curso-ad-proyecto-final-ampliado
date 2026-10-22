# hogares/domain/exceptions/ya_es_miembro_exception.py (módulos 71 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class YaEsMiembroException(DominioException):
    codigo = "ya_es_miembro"
    mensaje = "Ya perteneces a este hogar."
