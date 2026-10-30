# asistente/domain/vo/ayuda_consultada.py — lo que deja buscar_ayuda para la interfaz y la contabilidad (100, ej. 1 y 2)
from dataclasses import dataclass

from asistente.domain.vo.respuesta_llm import RespuestaLLM


@dataclass(frozen=True, slots=True)
class AyudaConsultada:
    fuentes: tuple[tuple[str, str], ...]  # (documento#sección, título del documento): las secciones citadas
    llamadas: tuple[RespuestaLLM, ...] = ()  # las del modelo auxiliar (reescribir y ordenar): se pagan
