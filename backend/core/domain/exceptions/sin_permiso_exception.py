# core/domain/exceptions/sin_permiso_exception.py (módulo 87)
from core.domain.exceptions.dominio_exception import DominioException


class SinPermisoException(DominioException):
    codigo = "sin_permiso"
    status = 403
    mensaje = "Tu rol en este hogar no permite esta acción."
