# asistente/application/agent/limites.py — las guardas del agent loop (módulos 94, 96 y 99)
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
    # Módulo 96: tokens (estimados) del historial que viaja en cada llamada; lo que no quepa, fuera (ventana.py)
    max_tokens_historial: int = 3000
    # Módulo 99: tokens (estimados) de los resultados de tools de ESTA pregunta; pasados, los más antiguos se retiran
    # (aligerar.py). None: nunca. Por encima de lo que ocupan las preguntas normales: es para las que encadenan muchas
    max_tokens_resultados: int | None = 4000

    def __post_init__(self):
        if self.max_iteraciones < 2:  # una para pedir tools y otra para contestar con sus resultados
            raise ValueError("Hacen falta al menos 2 iteraciones.")
