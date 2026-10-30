# asistente/infrastructure/database/repositories/indice_de_ayuda_pg.py — la ayuda en PostgreSQL (módulo 100)
"""pgvector para los vectores y la búsqueda de texto de PostgreSQL para las palabras: los dos índices en la misma base
de datos que el resto de Gastos (sin otro servicio que desplegar, copiar en las copias de seguridad ni vigilar). Para
unos cientos de trozos, sobra; para millones, se mira un servicio de búsqueda dedicado."""

import re

from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from pgvector.django import CosineDistance

from asistente.domain.read_models.pasaje_encontrado import PasajeEncontrado
from asistente.domain.repositories.i_indice_de_ayuda import IIndiceDeAyuda
from asistente.domain.services.normalizar import sin_tildes
from asistente.infrastructure.database.models.trozo_de_ayuda_model import TrozoDeAyuda as TrozoModel

# Palabras que no buscan nada (y que el diccionario de PostgreSQL ya quita, pero no las de la pregunta: "cómo", "puedo")
VACIAS = frozenset("como cual cuales donde cuando que quien puedo puede quiero hay hacer hago tengo me mi mis".split())


class IndiceDeAyudaPG(IIndiceDeAyuda):
    def huellas(self):
        return {c: (h, m) for c, h, m in TrozoModel.objects.values_list("clave", "huella", "modelo")}

    def guardar(self, trozos, vectores, modelo):
        for n, t in enumerate(trozos):
            TrozoModel.objects.update_or_create(
                clave=t.clave,
                defaults={
                    "documento": t.documento,
                    "seccion": t.seccion,
                    "titulo": t.titulo,
                    "texto": t.texto,
                    "normalizado": sin_tildes(t.para_indexar),
                    "huella": t.huella,
                    "modelo": modelo if vectores is not None else "",
                    "embedding": vectores[n] if vectores is not None else None,
                },
            )

    def borrar(self, claves):
        TrozoModel.objects.filter(clave__in=claves).delete()

    def buscar_por_texto(self, consulta, limite):
        palabras = [p for p in re.findall(r"\w+", sin_tildes(consulta)) if p not in VACIAS and len(p) > 1]
        if not palabras:
            return []
        # OR y no AND (lo de websearch): una pregunta tiene palabras que la ayuda no usa, y con AND no saldría nada.
        # Ordena ts_rank: los que tienen más palabras, y más raras, primero
        query = SearchQuery(" | ".join(palabras), search_type="raw", config="spanish")
        filas = (
            TrozoModel.objects.filter(busqueda=query)
            .annotate(puntos=SearchRank(F("busqueda"), query))
            .order_by("-puntos", "clave")[:limite]
        )
        return [_pasaje(f, f.puntos) for f in filas]

    def buscar_por_vector(self, vector, modelo, limite):
        filas = (
            TrozoModel.objects.filter(modelo=modelo, embedding__isnull=False)
            .annotate(distancia=CosineDistance("embedding", vector))
            .order_by("distancia", "clave")[:limite]
        )
        return [_pasaje(f, 1 - f.distancia) for f in filas]


def _pasaje(f: TrozoModel, puntuacion: float) -> PasajeEncontrado:
    return PasajeEncontrado(f.clave, f"{f.documento}#{f.seccion}", f.titulo, f.texto, float(puntuacion))
