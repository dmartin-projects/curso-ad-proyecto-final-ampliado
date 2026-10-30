# asistente/domain/vo/intercambio.py — una pregunta y su respuesta, como las ve la persona (módulo 99)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Intercambio:
    """Lo que se resume: el texto visible, sin tool calls ni resultados (como viajan las preguntas anteriores, módulo
    96). `hasta` es el id del último mensaje del intercambio: donde acaba lo que el resumen ya cuenta."""

    pregunta: str
    respuesta: str
    hasta: int
