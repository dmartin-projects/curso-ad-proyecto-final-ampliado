# estadisticas/domain/exceptions/esquema_desconocido_exception.py (módulos 85 y 89)
#
# Cada excepción del servicio lleva su decisión: parar, aparcar o devolver un 422.


class EsquemaDesconocidoException(Exception):
    """Un mensaje con un formato que este servicio todavía no entiende (módulo 85, §4).

    El consumidor se PARA en vez de saltárselo: se actualiza el servicio y, al volver, sigue por ese mensaje.
    """
