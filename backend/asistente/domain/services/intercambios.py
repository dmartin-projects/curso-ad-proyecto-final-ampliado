# asistente/domain/services/intercambios.py — los mensajes visibles, en preguntas con su respuesta (módulo 99)
from collections.abc import Iterable

from asistente.domain.vo.intercambio import Intercambio


def emparejar(visibles: Iterable[tuple[int, str, str]]) -> tuple[Intercambio, ...]:
    """(id, rol, texto) en orden → Intercambio por cada pregunta con respuesta. Una pregunta sin respuesta (la que se
    está contestando ahora, o una cancelada) no forma intercambio: no hay nada que resumir de ella."""
    intercambios, pregunta = [], None
    for id_, rol, texto in visibles:
        if rol == "usuario":
            pregunta = texto
        elif rol == "modelo" and pregunta is not None:
            intercambios.append(Intercambio(pregunta, texto, id_))
            pregunta = None
    return tuple(intercambios)
