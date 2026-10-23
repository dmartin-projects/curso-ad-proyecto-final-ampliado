# usuarios/domain/exceptions/sesion_cerrada_exception.py — (módulo 92)
from core.domain.exceptions.dominio_exception import DominioException


class SesionCerradaException(DominioException):
    codigo = "sesion_cerrada"
    status = 401
    mensaje = "La sesión se ha cerrado. Vuelve a entrar."
