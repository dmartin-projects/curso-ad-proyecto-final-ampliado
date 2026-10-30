# asistente/domain/exceptions/analisis_detenido_exception.py (ejercicios 1 y 2 del 105)
class AnalisisDetenidoException(Exception):
    """El análisis se para entre especialista y especialista: lo ha cancelado la persona ("cancelado") o ha llegado a
    su tope de tokens ("tope"). Como PreguntaCanceladaException (módulo 97), no es un error de nadie."""

    def __init__(self, motivo: str):
        super().__init__(motivo)
        self.motivo = motivo
