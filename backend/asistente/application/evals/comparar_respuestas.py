# asistente/application/evals/comparar_respuestas.py — A frente a B, en los dos órdenes (ejercicio 3 del 103)
"""Comparar dos respuestas (dos modelos, dos versiones del prompt) es más fiable que puntuar cada una por su cuenta,
pero tiene un sesgo conocido: el de POSICIÓN (muchos jueces prefieren la primera que leen). El remedio: preguntar dos
veces, cambiando el orden. Si las dos dicen lo mismo, vale; si se contradicen, es empate (el juez no sabe).
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, ValidationError

from asistente.application.ports.i_llm import ILLM
from asistente.application.prompts.comparar import COMPARAR
from asistente.application.tools.esquema_json import esquema_json
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM


class _Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    razonamiento: str
    mejor: Literal["A", "B", "empate"]


ESQUEMA = EsquemaRespuesta("comparacion", esquema_json(_Decision))


def _una_vez(llm: ILLM, pregunta: str, rubrica: str, a: str, b: str) -> str:
    mensaje = f"<pregunta>{pregunta}</pregunta>\n<rubrica>{rubrica}</rubrica>\n<A>{a}</A>\n<B>{b}</B>"
    r = llm.generar(
        PeticionLLM(sistema=COMPARAR.rellenar(), mensajes=(Mensaje.usuario(mensaje),), esquema=ESQUEMA, temperatura=0)
    )
    try:
        return _Decision.model_validate_json(r.texto).mejor
    except ValidationError:
        return "empate"


def comparar(llm: ILLM, pregunta: str, rubrica: str, primera: str, segunda: str) -> str:
    """ "primera", "segunda", "empate" o "inconsistente" (cada orden dice una cosa: sesgo de posición)."""
    ida = _una_vez(llm, pregunta, rubrica, primera, segunda)  # primera = A
    vuelta = _una_vez(llm, pregunta, rubrica, segunda, primera)  # primera = B
    traducir = {("A", "B"): "primera", ("B", "A"): "segunda", ("empate", "empate"): "empate"}
    return traducir.get((ida, vuelta), "inconsistente")
