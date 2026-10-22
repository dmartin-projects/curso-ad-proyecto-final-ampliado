# estadisticas/application/ports/i_unidad_de_trabajo.py — la transacción del use case (módulo 89)
from abc import ABC, abstractmethod
from contextlib import AbstractContextManager


class IUnidadDeTrabajo(ABC):
    """`with self.uow:` todo lo que pasa dentro se confirma junto o no se confirma."""

    @abstractmethod
    def __enter__(self) -> object: ...

    @abstractmethod
    def __exit__(self, *excepcion) -> bool | None: ...

    @abstractmethod
    def savepoint(self) -> AbstractContextManager:
        """Una transacción dentro de la transacción: si falla lo de dentro, se deshace solo eso."""
