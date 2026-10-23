# usuarios/domain/exceptions/mfa_no_activo_exception.py — (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class MfaNoActivoException(DominioException):
    codigo = "mfa_no_activo"
    status = 409
    mensaje = "La verificación en dos pasos no está activa."
