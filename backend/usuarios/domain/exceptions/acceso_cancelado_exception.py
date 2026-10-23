# usuarios/domain/exceptions/acceso_cancelado_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class AccesoCanceladoException(DominioException):
    codigo = "acceso_cancelado"
    status = 400
    mensaje = "Has cancelado el inicio de sesión."
