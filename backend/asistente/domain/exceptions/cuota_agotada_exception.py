# asistente/domain/exceptions/cuota_agotada_exception.py (módulo 98)
from core.domain.exceptions.dominio_exception import DominioException


class CuotaAgotadaException(DominioException):
    """Un 429 con Retry-After (`segundos`, en el contexto): el manejador de errores de la API ya sabe ponerlo."""

    codigo = "cuota_agotada"
    status = 429
    mensaje = "Has llegado al límite del asistente."
