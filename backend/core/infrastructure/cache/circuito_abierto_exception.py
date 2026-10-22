# core/infrastructure/cache/circuito_abierto_exception.py (módulos 27 y 88)
class CircuitoAbiertoException(Exception):
    """El circuito está abierto: no se llama al servicio hasta que pase el enfriamiento."""
