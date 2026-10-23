# usuarios/domain/exceptions/login_pendiente_no_valido_exception.py — (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class LoginPendienteNoValidoException(DominioException):
    """Sin la cookie del primer paso, caducada, agotada o de otro canal: hay que volver a empezar."""

    codigo = "login_pendiente_no_valido"
    status = 401
    mensaje = "El inicio de sesión ha caducado. Vuelve a entrar."
