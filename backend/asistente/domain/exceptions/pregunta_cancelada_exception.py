# asistente/domain/exceptions/pregunta_cancelada_exception.py — la persona se ha ido (módulo 97)
class PreguntaCanceladaException(Exception):
    """Ha cerrado la pestaña o ha pulsado "Detener": se deja de trabajar (y de pagar al modelo) en cuanto se puede. No es
    un error de nadie, por eso no hereda de DominioException ni de LLMException."""
