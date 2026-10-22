# finanzas/application/ports/i_reconocedor_comercios.py — un servicio que usa la aplicación (módulos 74, 87 y 88)
from abc import ABC, abstractmethod


class IReconocedorComercios(ABC):
    @abstractmethod
    def reconocer(self, texto: str) -> int | None:
        """El id del comercio conocido que más se parece al texto ("MERCADONA SA 0042" → Mercadona), o None."""

    # ── Módulo 88: para los procesos (tickets, extractos), que apuntan con ApuntarMovimientosUseCase ──
    @abstractmethod
    def reconocer_o_crear(self, nombre: str, nif: str = "") -> tuple[int, str] | None:
        """(id, nombre comercial) del comercio; si no se conoce, se da de alta. None si el nombre está vacío.

        Solo para nombres comerciales de verdad (los que lee la IA en un ticket): el catálogo de comercios es
        GLOBAL, lo ven todos los hogares en el autocompletado.
        """

    @abstractmethod
    def categoria_habitual(self, hogar_id: int, comercio_id: int | None, sugerida: str = "") -> int | None:
        """La categoría que ESTE hogar suele poner a ese comercio; si no hay costumbre, la `sugerida` (por nombre)."""
