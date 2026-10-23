# usuarios/domain/exceptions/email_no_verificado_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class EmailNoVerificadoException(DominioException):
    codigo = "email_no_verificado"
    status = 403
    mensaje = "Tu cuenta del proveedor no tiene un email verificado."
