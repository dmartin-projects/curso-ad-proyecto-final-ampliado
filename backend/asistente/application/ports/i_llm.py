# asistente/application/ports/i_llm.py — el port LLM: lo ÚNICO que el asistente sabe de un modelo (módulo 93)
from abc import ABC, abstractmethod

from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM


class ILLM(ABC):
    """Un turno del modelo a partir de una petición. Lo implementan OpenAICompatibleLLM (Groq, o cualquier API
    compatible con Chat Completions), LLMFake en los tests y, en el módulo 106, el adapter de Claude.

    Cambiar de proveedor es escribir otro adapter: ni el agent loop ni las tools se enteran.
    """

    @property
    @abstractmethod
    def modelo(self) -> str:
        """El modelo principal (para los logs y el coste)."""

    @abstractmethod
    def generar(self, peticion: PeticionLLM) -> RespuestaLLM:
        """Una llamada: la petición entera dentro, un turno del modelo fuera.

        Lanza LLMNoDisponibleException (transitorio) o PeticionLLMException (la petición está mal), nunca los
        errores de un SDK.
        """
