# asistente/domain/repositories/i_indice_de_ayuda.py — los trozos de la ayuda, indexados (módulo 100)
from abc import ABC, abstractmethod
from collections.abc import Sequence

from asistente.domain.read_models.pasaje_encontrado import PasajeEncontrado
from asistente.domain.vo.trozo_de_ayuda import TrozoDeAyuda


class IIndiceDeAyuda(ABC):
    """Un índice que se puede RECONSTRUIR desde los .md en cualquier momento: no es la fuente de verdad (lo son los
    archivos), es una copia preparada para buscar. Por eso se puede borrar sin miedo."""

    @abstractmethod
    def huellas(self) -> dict[str, tuple[str, str]]:
        """{clave: (huella del texto, modelo de embeddings con que se calculó su vector, o "")}."""

    @abstractmethod
    def guardar(self, trozos: Sequence[TrozoDeAyuda], vectores: Sequence[list[float]] | None, modelo: str) -> None:
        """Crea o actualiza (por clave). Sin vectores: solo la búsqueda por texto."""

    @abstractmethod
    def borrar(self, claves: Sequence[str]) -> None: ...

    @abstractmethod
    def buscar_por_texto(self, consulta: str, limite: int) -> list[PasajeEncontrado]:
        """Búsqueda léxica (palabras, con su raíz: «importé» encuentra «importar»)."""

    @abstractmethod
    def buscar_por_vector(self, vector: list[float], modelo: str, limite: int) -> list[PasajeEncontrado]:
        """Los más cercanos por similitud del coseno, solo entre los trozos embebidos con ese modelo."""
