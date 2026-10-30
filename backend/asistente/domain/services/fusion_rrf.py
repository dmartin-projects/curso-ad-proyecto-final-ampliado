# asistente/domain/services/fusion_rrf.py — juntar varias búsquedas en un orden (módulo 100)
"""Reciprocal Rank Fusion (Cormack, Clarke y Büttcher, 2009). Cada búsqueda da un orden; cada resultado suma 1/(k +
posición) por cada búsqueda en la que aparece. No mira las puntuaciones (la similitud del coseno y ts_rank no son
comparables: escalas distintas), solo las posiciones: lo que aparece arriba en las dos, gana. k = 60 es el del
artículo: suaviza la ventaja del primer puesto."""

from collections.abc import Iterable, Sequence


def fusionar[T](ordenes: Iterable[Sequence[T]], clave=lambda x: x, k: int = 60) -> list[T]:
    puntos: dict = {}
    primero: dict = {}
    for orden in ordenes:
        for posicion, elemento in enumerate(orden, start=1):
            c = clave(elemento)
            puntos[c] = puntos.get(c, 0.0) + 1 / (k + posicion)
            primero.setdefault(c, elemento)
    return [primero[c] for c in sorted(puntos, key=lambda c: -puntos[c])]
