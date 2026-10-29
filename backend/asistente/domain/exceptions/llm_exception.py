# asistente/domain/exceptions/llm_exception.py — el LLM no ha podido responder (módulo 93)
class LLMException(Exception):
    """Base de los errores del LLM. El resto del asistente solo conoce estas, nunca las de un SDK."""
