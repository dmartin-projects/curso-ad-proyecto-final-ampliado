# estadisticas/domain/repositories/i_membresia_command_repository.py — el lado de ESCRITURA (CQRS, módulo 89)
#
# La misma regla que los movimientos: solo gana una versión más nueva.
from abc import ABC, abstractmethod

from estadisticas.domain.bo.membresia import Membresia


class IMembresiaCommandRepository(ABC):
    @abstractmethod
    def guardar(self, membresia: Membresia) -> bool: ...

    @abstractmethod
    def eliminar(self, hogar_id: int, usuario_id: int, version: int) -> bool: ...

    @abstractmethod
    def vaciar(self) -> None: ...
