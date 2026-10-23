# usuarios/domain/exceptions/segundo_factor_bloqueado_hasta_recuperar_exception.py — (módulo 92)
from usuarios.domain.exceptions.segundo_factor_bloqueado_exception import SegundoFactorBloqueadoException


class SegundoFactorBloqueadoHastaRecuperarException(SegundoFactorBloqueadoException):
    """El techo de fallos seguidos (TECHO_DE_FALLOS): ya no se espera, se recupera la cuenta. Sin Retry-After."""

    codigo = "segundo_factor_bloqueado_hasta_recuperar"
    mensaje = (
        "Demasiados intentos fallidos seguidos: la verificación en dos pasos está bloqueada. Para desbloquearla, "
        "recupera tu contraseña con «¿Has olvidado tu contraseña?»."
    )
