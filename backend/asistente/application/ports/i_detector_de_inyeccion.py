# asistente/application/ports/i_detector_de_inyeccion.py — ¿este texto le habla al modelo? (módulo 102)
from abc import ABC, abstractmethod


class IDetectorDeInyeccion(ABC):
    """Un clasificador de prompt injection: la probabilidad (0 a 1) de que un texto intente dar instrucciones a un
    modelo en vez de ser datos. Lo implementan DetectorPromptGuard (Llama Prompt Guard 2, en Groq) y, en los tests,
    DetectorFake.

    Es una capa más, no LA barrera: se equivoca en los dos sentidos, y un atacante prueba hasta que pasa."""

    @property
    @abstractmethod
    def modelo(self) -> str:
        """Para los logs."""

    @abstractmethod
    def puntuar(self, texto: str) -> float:
        """La puntuación del texto entero (si es largo, la del peor trozo). Lanza LLMException si no puede."""
