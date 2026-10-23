# usuarios/domain/exceptions/login_social_no_valido_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class LoginSocialNoValidoException(DominioException):
    """El proveedor no ha dado una respuesta en la que se pueda confiar (code rechazado, ID token no válido…)."""

    codigo = "login_social_no_valido"
    status = 400
    mensaje = "No se ha podido completar el inicio de sesión con el proveedor. Vuelve a intentarlo."
