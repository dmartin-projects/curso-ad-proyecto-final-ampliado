# finanzas/application/ports/i_reconocedor_comercios.py — un servicio que usa la aplicación (módulos 74 y 87)
from abc import ABC, abstractmethod


class IReconocedorComercios(ABC):
    @abstractmethod
    def reconocer(self, texto: str) -> int | None:
        """El id del comercio conocido que más se parece al texto ("MERCADONA SA 0042" → Mercadona), o None."""
