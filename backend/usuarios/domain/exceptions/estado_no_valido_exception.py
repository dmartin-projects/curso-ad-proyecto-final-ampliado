# usuarios/domain/exceptions/estado_no_valido_exception.py (módulo 91)
from core.domain.exceptions.dominio_exception import DominioException


class EstadoNoValidoException(DominioException):
    """Sin la cookie del inicio de sesión, con otro `state`, caducada o ya usada: esta vuelta no es de una petición
    que hayamos empezado aquí (o ya se usó)."""

    codigo = "estado_no_valido"
    status = 400
    mensaje = "El inicio de sesión ha caducado o no se empezó aquí. Vuelve a intentarlo."
