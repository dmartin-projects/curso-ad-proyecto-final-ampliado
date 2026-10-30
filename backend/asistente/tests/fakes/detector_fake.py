# asistente/tests/fakes/detector_fake.py — un clasificador de inyecciones con reglas fijas (módulo 102)
from asistente.application.ports.i_detector_de_inyeccion import IDetectorDeInyeccion
from asistente.domain.exceptions.llm_no_disponible_exception import LLMNoDisponibleException

PALABRAS = ("ignora", "ignore", "instrucciones", "instructions", "system prompt")


class DetectorFake(IDetectorDeInyeccion):
    """0,99 si el texto lleva alguna de PALABRAS; 0,01 si no. Apunta lo que revisa (spy). Con `caido`, no responde."""

    def __init__(self, caido: bool = False):
        self.caido = caido
        self.revisados: list[str] = []

    @property
    def modelo(self) -> str:
        return "detector-fake"

    def puntuar(self, texto: str) -> float:
        self.revisados.append(texto)
        if self.caido:
            raise LLMNoDisponibleException("detector-fake: caído")
        return 0.99 if any(p in texto.lower() for p in PALABRAS) else 0.01
