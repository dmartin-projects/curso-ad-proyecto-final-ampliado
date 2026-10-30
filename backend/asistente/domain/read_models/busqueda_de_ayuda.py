# asistente/domain/read_models/busqueda_de_ayuda.py — lo que devuelve una búsqueda en la ayuda (módulo 100)
from dataclasses import dataclass

from asistente.domain.read_models.pasaje_encontrado import PasajeEncontrado
from asistente.domain.vo.respuesta_llm import RespuestaLLM


@dataclass(frozen=True, slots=True)
class BusquedaDeAyuda:
    pasajes: tuple[PasajeEncontrado, ...]  # los que contestan, del mejor al peor (puede no haber ninguno)
    consulta: str  # la búsqueda reescrita ("" si no se reescribió)
    modo: str  # "híbrida" (vectores y texto) o "texto" (sin embeddings: el fallback)
    candidatos: tuple[PasajeEncontrado, ...] = ()  # antes de reordenar: para evaluar cada paso por separado
    llamadas: tuple[RespuestaLLM, ...] = ()  # las del modelo auxiliar (reescribir y ordenar): para su coste
