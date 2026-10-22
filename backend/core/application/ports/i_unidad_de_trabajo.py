# core/application/ports/i_unidad_de_trabajo.py — la transacción del use case (módulo 87)
from abc import ABC, abstractmethod


class IUnidadDeTrabajo(ABC):
    """`with self.uow:` todo lo que pasa dentro se confirma junto o no se confirma."""

    @abstractmethod
    def __enter__(self) -> None: ...

    @abstractmethod
    def __exit__(self, *excepcion) -> bool | None: ...
