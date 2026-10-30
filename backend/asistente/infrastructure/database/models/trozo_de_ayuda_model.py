# asistente/infrastructure/database/models/trozo_de_ayuda_model.py — el índice de la ayuda (módulo 100)
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVector, SearchVectorField
from django.db import models
from pgvector.django import HnswIndex, VectorField

DIMENSION = 384  # la del modelo de embeddings (paraphrase-multilingual-MiniLM-L12-v2): otro modelo, otra migración


class TrozoDeAyuda(models.Model):
    """Una copia de un trozo de los .md de la ayuda, preparada para buscar de dos formas:

    - `embedding`: su vector (pgvector), con el índice HNSW para buscar los más cercanos por coseno sin recorrer todos;
    - `busqueda`: su tsvector (la búsqueda de texto de PostgreSQL, con las raíces del castellano), generado por la base
      de datos a partir de `normalizado` (sin tildes: "comun" encuentra "común"), con su índice GIN.
    """

    clave = models.CharField(max_length=300, unique=True)  # documento#sección#parte
    documento = models.CharField(max_length=100)
    seccion = models.CharField(max_length=200)
    titulo = models.CharField(max_length=200)
    texto = models.TextField()
    normalizado = models.TextField()  # título, sección y texto, sin tildes ni mayúsculas (lo calcula el repositorio)
    huella = models.CharField(max_length=16)
    modelo = models.CharField(max_length=200, blank=True)  # el de su vector ("" si no tiene)
    embedding = VectorField(dimensions=DIMENSION, null=True, blank=True)
    busqueda = models.GeneratedField(
        expression=SearchVector("normalizado", config="spanish"), output_field=SearchVectorField(), db_persist=True
    )

    class Meta:
        indexes = [
            HnswIndex(
                name="asistente_ayuda_vector",
                fields=["embedding"],
                m=16,
                ef_construction=64,
                opclasses=["vector_cosine_ops"],
            ),
            GinIndex(fields=["busqueda"], name="asistente_ayuda_texto"),
        ]

    def __str__(self):
        return self.clave
