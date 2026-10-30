# asistente/application/ports/i_llm.py — el port LLM: lo ÚNICO que el asistente sabe de un modelo (módulos 93 y 97)
from abc import ABC, abstractmethod
from collections.abc import Callable

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

    def generar_en_streaming(self, peticion: PeticionLLM, al_texto: Callable[[str], None]) -> RespuestaLLM:
        """Módulo 97: lo mismo, pero el texto visible va saliendo por `al_texto` según lo genera el modelo (el chat lo
        enseña mientras llega). Devuelve la misma RespuestaLLM completa al final. Si `al_texto` lanza una excepción
        (la persona ha cancelado), se deja de leer y la excepción sale tal cual.

        Por defecto, sin streaming: el texto entero de una vez, al final. Un adapter que sabe hacerlo lo sobrescribe
        (OpenAICompatibleLLM); los demás (LLMFake) funcionan igual, solo que de golpe."""
        respuesta = self.generar(peticion)
        if respuesta.texto:
            al_texto(respuesta.texto)
        return respuesta
