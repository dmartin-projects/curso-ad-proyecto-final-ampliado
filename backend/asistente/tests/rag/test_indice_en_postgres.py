"""Módulo 100: el índice en PostgreSQL de verdad: pgvector (coseno, con el índice HNSW) y la búsqueda de texto en
castellano (raíces y sin tildes)."""

import pytest
from django.db import connection

from asistente.application.indexar_ayuda_use_case.dtos.indexar_ayuda_input_dto import IndexarAyudaInputDTO
from asistente.application.indexar_ayuda_use_case.indexar_ayuda_use_case import IndexarAyudaUseCase
from asistente.infrastructure.ayuda.fuente_de_ayuda_en_disco import FuenteDeAyudaEnDisco
from asistente.infrastructure.database.repositories.indice_de_ayuda_pg import IndiceDeAyudaPG
from asistente.tests.fakes.embeddings_fake import EmbeddingsFake
from core.infrastructure.database.unidad_de_trabajo_django import UnidadDeTrabajoDjango

pytestmark = pytest.mark.django_db


@pytest.fixture
def indice():
    embeddings = EmbeddingsFake()
    IndexarAyudaUseCase(
        fuente=FuenteDeAyudaEnDisco(), indice=IndiceDeAyudaPG(), embeddings=embeddings, uow=UnidadDeTrabajoDjango()
    ).ejecutar(IndexarAyudaInputDTO())
    return IndiceDeAyudaPG(), embeddings


def test_texto_con_raices_y_sin_tildes(indice):
    pg, _ = indice
    fuentes = [p.fuente for p in pg.buscar_por_texto("IMPORTÉ el extracto dos veces", 3)]
    assert "importar-extractos#Sin duplicados" in fuentes  # "importé" → "import", y "veces" → "vec"
    assert pg.buscar_por_texto("¿cómo puedo?", 3) == []  # solo palabras vacías: nada que buscar


def test_vector_con_coseno_solo_del_mismo_modelo(indice):
    pg, embeddings = indice
    [primero, *_] = pg.buscar_por_vector(embeddings.consulta("passkey huella"), "fake-384", 3)
    assert primero.fuente == "seguridad-de-la-cuenta#Passkeys" and 0 < primero.puntuacion <= 1
    assert pg.buscar_por_vector(embeddings.consulta("passkey"), "otro-modelo", 3) == []


def test_los_indices_existen():
    with connection.cursor() as c:
        c.execute("select indexname, indexdef from pg_indexes where tablename = 'asistente_trozodeayuda'")
        indices = dict(c.fetchall())
    assert "USING hnsw (embedding vector_cosine_ops)" in indices["asistente_ayuda_vector"]
    assert "USING gin (busqueda)" in indices["asistente_ayuda_texto"]
