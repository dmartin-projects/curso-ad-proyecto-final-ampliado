# core/domain/read_models/pagina.py — una página de resultados, la devuelva quien la devuelva (módulo 87)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Pagina[T]:
    """Lo que devuelve un query service paginado: los read models de la página y cómo seguir.

    Dos formas de paginar, los mismos campos. Por número (`Paginacion`): `count`, `numero`, `total_paginas` y
    `siguiente`/`anterior` con el número de la página ("3"). Por cursor (`PaginacionCursor`): sin `count` (contar
    toda la tabla es justo lo que el cursor evita) y `siguiente`/`anterior` con un cursor opaco. None: no hay más.
    """

    results: list[T]
    tamano: int
    siguiente: str | None = None
    anterior: str | None = None
    count: int | None = None
    numero: int | None = None
    total_paginas: int | None = None
