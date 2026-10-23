# usuarios/domain/exceptions/cuenta_desactivada_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class CuentaDesactivadaException(DominioException):
    codigo = "cuenta_desactivada"
    status = 403
    mensaje = "Esta cuenta está desactivada."
