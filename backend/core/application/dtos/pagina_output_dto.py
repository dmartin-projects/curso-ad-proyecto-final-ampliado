# core/application/dtos/pagina_output_dto.py — la página que devuelve un use case de consulta (módulo 87)
from collections.abc import Callable
from dataclasses import dataclass

from core.domain.read_models.pagina import Pagina


@dataclass(frozen=True, slots=True)
class PaginaOutputDTO[T]:
    """Los mismos campos que el read model `Pagina`, con OutputDTOs en `results`."""

    results: list[T]
    tamano: int
    siguiente: str | None = None
    anterior: str | None = None
    count: int | None = None
    numero: int | None = None
    total_paginas: int | None = None

    @classmethod
    def desde_pagina[R](cls, pagina: Pagina[R], convertir: Callable[[R], T]) -> "PaginaOutputDTO[T]":
        return cls(
            results=[convertir(r) for r in pagina.results],
            tamano=pagina.tamano,
            siguiente=pagina.siguiente,
            anterior=pagina.anterior,
            count=pagina.count,
            numero=pagina.numero,
            total_paginas=pagina.total_paginas,
        )
