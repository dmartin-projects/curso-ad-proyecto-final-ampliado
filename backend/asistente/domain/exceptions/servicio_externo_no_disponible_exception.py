# asistente/domain/exceptions/servicio_externo_no_disponible_exception.py — un servicio de terceros no responde (módulo 95)
class ServicioExternoNoDisponibleException(Exception):
    """Timeout, error de red o 5xx de un servicio externo (tipos de cambio, precios…), tras sus reintentos.

    No es un error del usuario ni del modelo: la tool lo convierte en un mensaje que le dice al modelo que NO invente el
    dato y se lo explique al usuario."""

    def __init__(self, servicio: str, detalle: str = ""):
        super().__init__(f"{servicio}: {detalle}" if detalle else servicio)
        self.servicio = servicio
