# estadisticas/domain/exceptions/evento_invalido_exception.py (módulos 85 y 89)


class EventoInvalidoException(Exception):
    """Un evento que NUNCA se va a poder aplicar: JSON roto, falta un campo, un importe "abc", un número que no
    cabe en la columna… Se aparca y se sigue. Guarda el error original (`causa`): es lo que se anota al aparcarlo.
    """

    def __init__(self, causa: Exception):
        super().__init__(repr(causa))
        self.causa = causa
