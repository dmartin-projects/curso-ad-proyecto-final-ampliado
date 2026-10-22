# finanzas/domain/repositories/i_categoria_command_repository.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.domain.bo.categoria import Categoria


class ICategoriaCommandRepository(ABC):
    @abstractmethod
    def obtener(self, hogar_id: int, categoria_id: int) -> Categoria:
        """De ESE hogar, o CategoriaNoEncontradaException."""

    @abstractmethod
    def del_hogar(self, hogar_id: int) -> list[Categoria]: ...

    @abstractmethod
    def tiene_hijas(self, categoria_id: int) -> bool: ...

    @abstractmethod
    def guardar(self, categoria: Categoria) -> None:
        """Inserta o actualiza. Un nombre repetido en el mismo nivel: CategoriaDuplicadaException."""

    @abstractmethod
    def crear_varias(self, categorias: list[Categoria]) -> None:
        """Inserta todas de una vez y les pone el id."""

    @abstractmethod
    def guardar_orden(self, categorias: list[Categoria]) -> None: ...

    @abstractmethod
    def eliminar(self, categoria: Categoria) -> None: ...
