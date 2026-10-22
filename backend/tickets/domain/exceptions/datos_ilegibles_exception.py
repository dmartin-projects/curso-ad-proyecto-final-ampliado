# tickets/domain/exceptions/datos_ilegibles_exception.py (módulos 74 y 88)
from core.domain.exceptions.dominio_exception import DominioException


class DatosIlegiblesException(DominioException):
    """La IA ha respondido, pero lo que dice no sirve (JSON roto, un total negativo…): reintentar no ayuda, el
    usuario completará los datos a mano. Lo lanza el adapter de la IA; los errores pasajeros (red, 503) no son
    esto: siguen su camino hasta la tarea de Celery, que reintenta."""

    codigo = "ticket_datos_ilegibles"
    mensaje = "La IA no ha devuelto datos válidos."
