# asistente/domain/exceptions/peticion_llm_exception.py — 400, 401, 403, 404, 413, 422 (módulo 93)
from asistente.domain.exceptions.llm_exception import LLMException


class PeticionLLMException(LLMException):
    """La petición está mal (la clave, el modelo, un schema que el proveedor no admite): reintentar no sirve."""
