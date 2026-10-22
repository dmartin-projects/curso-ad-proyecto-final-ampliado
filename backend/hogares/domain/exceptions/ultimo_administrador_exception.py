# hogares/domain/exceptions/ultimo_administrador_exception.py (módulos 71 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class UltimoAdministradorException(DominioException):
    codigo = "ultimo_administrador"
    mensaje = "Un hogar necesita al menos un administrador."
