# usuarios/domain/exceptions/identidad_de_otra_cuenta_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class IdentidadDeOtraCuentaException(DominioException):
    codigo = "identidad_de_otra_cuenta"
    status = 409
    mensaje = "Esa cuenta del proveedor ya está vinculada a otro usuario de Gastos."
