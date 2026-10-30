# asistente/application/chat/titular.py — el título de una conversación, con un modelo pequeño (módulo 97)
"""Tras la primera respuesta, una llamada aparte: sin tools, sin historial, solo la pregunta, con el modelo AUXILIAR
(gpt-oss-20b: más rápido, más barato y con su propia cuota en Groq). Es una tarea fácil: no merece el modelo grande.

Si falla, no pasa nada: la conversación se titula con el principio de la pregunta. Un título nunca tumba una respuesta.
"""

import logging

from asistente.application.ports.i_llm import ILLM
from asistente.application.prompts.titulo import TITULO
from asistente.domain.bo.conversacion import MAX_TITULO
from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM

logger = logging.getLogger(__name__)


def titulo_de_respaldo(pregunta: str) -> str:
    """El principio de la pregunta, cortado por una palabra entera."""
    texto = " ".join(pregunta.split())
    if len(texto) <= 60:
        return texto
    return texto[:60].rsplit(" ", 1)[0] + "…"


def titular(llm: ILLM, pregunta: str) -> tuple[str, RespuestaLLM | None]:
    """(título, la respuesta del modelo si la hubo: para sumar su uso)."""
    peticion = PeticionLLM(
        sistema="",
        mensajes=(Mensaje.usuario(TITULO.rellenar(pregunta=pregunta[:500])),),
        esfuerzo=EsfuerzoDeRazonamiento.BAJO,
        max_tokens=200,  # el razonamiento cuenta: con 30, un modelo que piensa no llega a escribir el título
    )
    try:
        r = llm.generar(peticion)
    except LLMException:
        logger.warning("Sin título automático: el LLM no está disponible", exc_info=True)
        return titulo_de_respaldo(pregunta), None
    titulo = r.texto.strip().strip("«»\"'.").strip()
    if not titulo or len(titulo) > MAX_TITULO or "\n" in titulo:
        return titulo_de_respaldo(pregunta), r
    return titulo, r
