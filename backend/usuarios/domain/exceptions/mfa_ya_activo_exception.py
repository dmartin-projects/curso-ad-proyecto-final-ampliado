# usuarios/domain/exceptions/mfa_ya_activo_exception.py — (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class MfaYaActivoException(DominioException):
    codigo = "mfa_ya_activo"
    status = 409
    mensaje = "La verificación en dos pasos ya está activa."
