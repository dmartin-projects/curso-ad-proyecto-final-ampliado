# asistente/application/ayuda/buscador_de_ayuda.py — la R de RAG: encontrar en la ayuda lo que contesta (módulo 100)
"""Cuatro pasos, cada uno porque el anterior falla de una forma concreta (medido con el conjunto de evaluación):

1. Reescribir la pregunta (modelo auxiliar): "¿y eso cómo lo quito?" no comparte palabras con la ayuda.
2. Buscar por SIGNIFICADO (vectores, pgvector) y por PALABRAS (texto, PostgreSQL), con la pregunta y con la búsqueda
   reescrita: cuatro listas. Los vectores encuentran "meter los movimientos del banco" → "importar el extracto"; el
   texto, lo exacto que los vectores difuminan ("passkey", "CSV", "gastos-cli").
3. Fusionarlas con RRF (solo las posiciones: las puntuaciones de cada búsqueda no se comparan).
4. Reordenar los mejores candidatos con el modelo auxiliar (reranking): de ocho, cuáles contestan de verdad, en orden.

Si los embeddings no están (el modelo no carga), el paso 2 es solo por texto: peor, pero funciona (el fallback). Si el
modelo auxiliar no está, se busca con la pregunta tal cual y se devuelve el orden de RRF.
"""

import logging

from pydantic import BaseModel, ConfigDict, ValidationError

from asistente.application.ports.i_embeddings import IEmbeddings
from asistente.application.ports.i_llm import ILLM
from asistente.application.prompts.ayuda import ORDENAR, REESCRIBIR
from asistente.application.tools.esquema_json import esquema_json
from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.exceptions.embeddings_no_disponibles_exception import EmbeddingsNoDisponiblesException
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.read_models.busqueda_de_ayuda import BusquedaDeAyuda
from asistente.domain.read_models.pasaje_encontrado import PasajeEncontrado
from asistente.domain.repositories.i_indice_de_ayuda import IIndiceDeAyuda
from asistente.domain.services.fusion_rrf import fusionar
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM

logger = logging.getLogger(__name__)
MAX_PASAJE = 700  # caracteres de cada candidato que lee el reordenador: lo justo para juzgar


class _Orden(BaseModel):
    model_config = ConfigDict(extra="forbid")
    relevantes: list[int]


ESQUEMA_ORDEN = EsquemaRespuesta("pasajes_relevantes", esquema_json(_Orden))


class BuscadorDeAyuda:
    def __init__(
        self,
        *,
        indice: IIndiceDeAyuda,
        embeddings: IEmbeddings | None,  # None: sin vectores (solo texto)
        llm: ILLM | None,  # el auxiliar; None: ni reescribir ni reordenar
        candidatos: int = 8,  # por búsqueda, y los que se reordenan
        devolver: int = 3,
    ):
        self.indice, self.embeddings, self.llm = indice, embeddings, llm
        self.candidatos, self.devolver = candidatos, devolver

    def buscar(self, pregunta: str, *, reescribir: bool = True, ordenar: bool = True) -> BusquedaDeAyuda:
        llamadas = []
        consulta = ""
        if reescribir and self.llm is not None:
            consulta, r = self._reescribir(pregunta)
            llamadas += [r] if r else []
        textos = [t for t in dict.fromkeys([pregunta, consulta]) if t]
        listas, modo = [], "híbrida"
        for texto in textos:
            listas.append(self.indice.buscar_por_texto(texto, self.candidatos))
        if self.embeddings is None:  # configurado así (los tests, el E2E): no es un fallo
            modo = "texto"
        else:
            try:
                for texto in textos:
                    vector = self.embeddings.consulta(texto)
                    listas.append(self.indice.buscar_por_vector(vector, self.embeddings.modelo, self.candidatos))
            except EmbeddingsNoDisponiblesException as e:  # el modelo no carga: se avisa, y se sigue por texto
                logger.warning("Búsqueda en la ayuda solo por texto: %s", e)
                modo = "texto"
        candidatos = fusionar(listas, clave=lambda p: p.clave)[: self.candidatos]
        pasajes = candidatos[: self.devolver]
        if ordenar and self.llm is not None and candidatos:
            ordenados, r = self._ordenar(pregunta, candidatos)
            if r is not None:
                llamadas.append(r)
            if ordenados is not None:
                pasajes = ordenados
        return BusquedaDeAyuda(tuple(pasajes), consulta, modo, tuple(candidatos), tuple(llamadas))

    def _reescribir(self, pregunta: str):
        peticion = PeticionLLM(
            sistema="",
            mensajes=(Mensaje.usuario(REESCRIBIR.rellenar(pregunta=pregunta[:500])),),
            esfuerzo=EsfuerzoDeRazonamiento.BAJO,
            max_tokens=300,
        )
        try:
            r = self.llm.generar(peticion)
        except LLMException:
            logger.warning("Sin reescritura de la búsqueda: el LLM no está disponible", exc_info=True)
            return "", None
        consulta = " ".join(r.texto.split())[:200] if r.motivo == MotivoFin.FIN else ""
        return consulta, r

    def _ordenar(self, pregunta: str, candidatos: list[PasajeEncontrado]):
        lista = "\n\n".join(
            f"[{n}] {p.titulo} · {p.fuente.split('#', 1)[1]}\n{p.texto[:MAX_PASAJE]}"
            for n, p in enumerate(candidatos, start=1)
        )
        peticion = PeticionLLM(
            sistema="",
            mensajes=(Mensaje.usuario(ORDENAR.rellenar(pregunta=pregunta[:500], pasajes=lista, maximo=self.devolver)),),
            esquema=ESQUEMA_ORDEN,
            esfuerzo=EsfuerzoDeRazonamiento.BAJO,
            max_tokens=400,
        )
        try:
            r = self.llm.generar(peticion)
            numeros = _Orden.model_validate_json(r.texto).relevantes
        except LLMException:
            logger.warning("Sin reordenar: el LLM no está disponible", exc_info=True)
            return None, None
        except ValidationError:  # strict lo garantiza; si aun así llega otra cosa, mejor el orden de RRF
            # Sin el texto: puede repetir la pregunta o los pasajes, y la pregunta puede llevar datos del hogar
            logger.warning("Reordenación no válida (%s caracteres): sigue el orden de RRF", len(r.texto))
            return None, r
        validos = [n for n in dict.fromkeys(numeros) if 1 <= n <= len(candidatos)]  # sin inventados ni repetidos
        return [candidatos[n - 1] for n in validos][: self.devolver], r
