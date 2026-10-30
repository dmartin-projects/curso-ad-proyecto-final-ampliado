"""Módulo 100: el adapter de embeddings sin el modelo en la caché. El chat no lo descarga: falla al momento, y la
búsqueda sigue por texto (el fallback). Sin red: es justo lo que se prueba."""

import time

import pytest

from asistente.domain.exceptions.embeddings_no_disponibles_exception import EmbeddingsNoDisponiblesException
from asistente.infrastructure.embeddings.embeddings_fastembed import EmbeddingsFastembed

MODELO = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


def test_sin_el_modelo_en_la_cache_falla_al_momento_sin_descargar(tmp_path):
    embeddings = EmbeddingsFastembed(modelo=MODELO, cache=str(tmp_path))  # descargar=False: lo del chat
    inicio = time.perf_counter()
    with pytest.raises(EmbeddingsNoDisponiblesException, match=MODELO):
        embeddings.consulta("¿cómo importo un extracto?")
    assert time.perf_counter() - inicio < 5  # descargando, sin red, serían ~40 s de reintentos
    assert not any(tmp_path.iterdir())  # y no ha bajado nada
