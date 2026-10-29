# asistente/application/agent/limites.py — las guardas del agent loop (módulo 94)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Limites:
    """Lo que separa un agente de producción de uno de blog: cada pregunta tiene un techo de vueltas, de tiempo y de
    tamaño de lo que lee. Un buen agente no llega casi nunca; uno que se tuerce, sí, y se paga por vuelta."""

    max_iteraciones: int = 6  # llamadas al LLM por pregunta; la última, sin tools
    segundos: float = (
        60.0  # pasado este tiempo, la siguiente vuelta es la última (sin tools): contesta con lo que tiene
    )
    max_caracteres_resultado: int = 6000  # ~1.500 tokens por resultado de tool: una red de seguridad
    # Ejercicio 1: pasados estos tokens (entrada + salida, sumando todas las vueltas), la siguiente vuelta es la última
    max_tokens: int | None = None

    def __post_init__(self):
        if self.max_iteraciones < 2:  # una para pedir tools y otra para contestar con sus resultados
            raise ValueError("Hacen falta al menos 2 iteraciones.")
