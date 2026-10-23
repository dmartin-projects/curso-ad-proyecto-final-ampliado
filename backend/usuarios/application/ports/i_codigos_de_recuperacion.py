# usuarios/application/ports/i_codigos_de_recuperacion.py (módulo 92)
from abc import ABC, abstractmethod


class ICodigosDeRecuperacion(ABC):
    @abstractmethod
    def generar(self, usuario_id: int) -> list[str]:
        """Diez nuevos (los anteriores dejan de valer). Se enseñan UNA vez: se guardan con hash."""

    @abstractmethod
    def usar(self, usuario_id: int, codigo: str) -> bool:
        """True si es uno de los suyos sin usar; y ya no vale más."""

    @abstractmethod
    def quedan(self, usuario_id: int) -> int: ...

    @abstractmethod
    def borrar(self, usuario_id: int) -> None: ...
