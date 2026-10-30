# asistente/infrastructure/embeddings/embeddings_fastembed.py — embeddings locales, en el proceso (módulo 100)
"""Groq no tiene embeddings, y la búsqueda no debería depender de otra API de pago con su clave, su cuota y su
latencia. fastembed ejecuta el modelo EN el proceso, con ONNX Runtime en la CPU (sin PyTorch: unos 60 MB en vez de
2 GB), y el modelo es:

    sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2   384 dimensiones, 50+ idiomas, Apache 2.0,
                                                                  cuantizado (≈ 240 MB), ~10 ms por frase en una CPU

multilingüe (la ayuda está en castellano y alguien preguntará en inglés), entrenado para PARÁFRASIS (justo lo que es
una pregunta frente a la ayuda que la contesta) y sin prefijos de "query:"/"passage:" (los e5 los necesitan).

Se descarga del Hub de Hugging Face a ASISTENTE_EMBEDDINGS_CACHE solo con `descargar` (manage.py indexar_ayuda; en
producción, al construir la imagen de Docker). Una pregunta del chat NUNCA descarga: si el modelo no está en la caché,
falla al momento (medido: medio segundo) y la búsqueda sigue por texto. Descargando, sin red, fastembed reintenta
durante unos 40 s: una pregunta que los esperara pasaría del límite de tiempo del agente (60 s, módulo 94).
"""

import functools
import logging
import threading

from asistente.application.ports.i_embeddings import IEmbeddings
from asistente.domain.exceptions.embeddings_no_disponibles_exception import EmbeddingsNoDisponiblesException

logger = logging.getLogger(__name__)
_cargando = threading.Lock()


class EmbeddingsFastembed(IEmbeddings):
    def __init__(self, *, modelo: str, cache: str | None = None, dimension: int = 384, descargar: bool = False):
        self._modelo, self._cache, self._dimension, self._descargar = modelo, cache, dimension, descargar

    @property
    def modelo(self) -> str:
        return self._modelo

    @property
    def dimension(self) -> int:
        return self._dimension

    def documentos(self, textos):
        return [list(map(float, v)) for v in self._cargado().embed(list(textos), batch_size=32)]

    def consulta(self, texto):
        return list(map(float, next(iter(self._cargado().query_embed(texto)))))

    def _cargado(self):
        try:
            return _modelo_del_proceso(self._modelo, self._cache, self._descargar)
        except Exception as e:  # sin red la primera vez, sin disco, un modelo que no existe…
            raise EmbeddingsNoDisponiblesException(f"{self._modelo}: {type(e).__name__}: {e}"[:300]) from e


@functools.lru_cache(maxsize=2)
def _modelo_del_proceso(modelo: str, cache: str | None, descargar: bool):
    """Uno por proceso (cargarlo cuesta ~1,5 s y ~600 MB de memoria), y con un candado: dos peticiones a la vez no lo
    cargan dos veces. Si falla, lru_cache no guarda el error: se volverá a intentar."""
    from fastembed import TextEmbedding  # aquí: importar fastembed carga onnxruntime, y no siempre hace falta

    with _cargando:
        logger.info("Cargando el modelo de embeddings %s", modelo)
        return TextEmbedding(model_name=modelo, cache_dir=cache, local_files_only=not descargar)
