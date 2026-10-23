# usuarios/domain/exceptions/ya_tiene_contrasena_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class YaTieneContrasenaException(DominioException):
    codigo = "ya_tiene_contrasena"
    status = 409
    mensaje = "Tu cuenta ya tiene contraseña."
