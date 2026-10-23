# usuarios/domain/exceptions/cuenta_ya_existe_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class CuentaYaExisteException(DominioException):
    codigo = "cuenta_existente"
    status = 409
    mensaje = "Ya hay una cuenta con ese email: entra como siempre y vincula el proveedor desde «Métodos de acceso»."
