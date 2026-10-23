# usuarios/domain/exceptions/segundo_factor_bloqueado_exception.py — (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class SegundoFactorBloqueadoException(DominioException):
    codigo = "segundo_factor_bloqueado"
    status = 429
    mensaje = "Demasiados intentos fallidos. Espera unos minutos y vuelve a probar."
