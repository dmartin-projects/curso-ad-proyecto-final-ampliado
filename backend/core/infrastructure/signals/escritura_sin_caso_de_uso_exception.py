# core/infrastructure/signals/escritura_sin_caso_de_uso_exception.py (módulo 88)
class EscrituraSinCasoDeUsoException(RuntimeError):
    """Se ha guardado o borrado con el ORM algo cuyos eventos solo publica un use case (la alarma)."""
