# eventos/domain/exceptions/publicacion_no_confirmada_exception.py (módulos 85 y 88)
class PublicacionNoConfirmadaException(Exception):
    """El broker no ha confirmado todo el lote: no se marca nada y se reintentará."""

    pass
