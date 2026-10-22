# hogares/domain/repositories/i_membresia_command_repository.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.domain.bo.membresia import Membresia


class IMembresiaCommandRepository(ABC):
    @abstractmethod
    def obtener(self, hogar_id: int, membresia_id: int, *, bloquear: bool = False) -> Membresia:
        """De ESE hogar, o MiembroNoEncontradoException."""

    @abstractmethod
    def admins(self, hogar_id: int) -> int:
        """Cuántos administradores tiene, con sus filas BLOQUEADAS hasta el final de la transacción."""

    @abstractmethod
    def es_miembro(self, hogar_id: int, *, usuario_id: int | None = None, email: str | None = None) -> bool: ...

    @abstractmethod
    def guardar(self, membresia: Membresia) -> None:
        """Inserta o actualiza. Ya era miembro (la UniqueConstraint membresia_unica): YaEsMiembroException."""

    @abstractmethod
    def eliminar(self, membresia: Membresia) -> None: ...
