# asistente/application/ports/i_embeddings.py — un texto, como un vector de números (módulo 100)
from abc import ABC, abstractmethod
from collections.abc import Sequence


class IEmbeddings(ABC):
    """Groq no tiene modelo de embeddings: el adapter es un modelo LOCAL (fastembed, en el proceso). Si mañana se usa
    una API de embeddings, es otro adapter, y el índice se reconstruye (un vector de un modelo no se compara con el de
    otro: por eso cada vector se guarda con el nombre de su modelo).

    Lanza EmbeddingsNoDisponiblesException si el modelo no se puede usar: quien busca sigue por texto."""

    @property
    @abstractmethod
    def modelo(self) -> str: ...

    @property
    @abstractmethod
    def dimension(self) -> int: ...

    @abstractmethod
    def documentos(self, textos: Sequence[str]) -> list[list[float]]:
        """Para indexar: varios de una vez (en lotes, es mucho más rápido). Normalizados (norma 1)."""

    @abstractmethod
    def consulta(self, texto: str) -> list[float]:
        """Para buscar. Algunos modelos tratan distinto la pregunta y el documento (los e5: "query:"/"passage:")."""
