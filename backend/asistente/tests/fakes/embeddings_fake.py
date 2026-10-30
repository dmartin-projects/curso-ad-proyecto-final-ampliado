# asistente/tests/fakes/embeddings_fake.py (módulo 100)
import hashlib
import math
import re

from asistente.application.ports.i_embeddings import IEmbeddings
from asistente.domain.exceptions.embeddings_no_disponibles_exception import EmbeddingsNoDisponiblesException
from asistente.domain.services.normalizar import sin_tildes

SINONIMOS = {"banco": "extracto", "pareja": "invitacion", "huella": "passkey"}  # lo que un modelo de verdad "sabe"


class EmbeddingsFake(IEmbeddings):
    """Determinista y sin modelo: cada palabra (sin tildes y con 5 letras como mucho, una raíz pobre) suma en una
    posición del vector; unas pocas palabras "saben" un sinónimo. Lo justo para probar el camino de los vectores en
    PostgreSQL y que una búsqueda sin palabras en común encuentre algo, que es lo que aportan."""

    def __init__(self, modelo: str = "fake-384", caido: bool = False):
        self._modelo, self.caido, self.llamadas = modelo, caido, 0

    @property
    def modelo(self):
        if self.caido:
            raise EmbeddingsNoDisponiblesException("modelo caído")
        return self._modelo

    @property
    def dimension(self):
        return 384

    def documentos(self, textos):
        return [self._vector(t) for t in textos]

    def consulta(self, texto):
        return self._vector(texto)

    def _vector(self, texto: str) -> list[float]:
        if self.caido:
            raise EmbeddingsNoDisponiblesException("modelo caído")
        self.llamadas += 1
        v = [0.0] * 384
        for palabra in re.findall(r"\w{3,}", sin_tildes(texto)):
            for p in (palabra, SINONIMOS.get(palabra, "")):
                if p:
                    v[int(hashlib.md5(p[:5].encode()).hexdigest(), 16) % 384] += 1.0
        norma = math.sqrt(sum(x * x for x in v)) or 1.0
        return [x / norma for x in v]
