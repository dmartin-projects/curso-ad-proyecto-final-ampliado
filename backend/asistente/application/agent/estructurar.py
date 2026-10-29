# asistente/application/agent/estructurar.py — la respuesta final, como JSON validado (módulo 96)
"""Structured output con tools, en dos pasos. Groq no deja pedir tools y un response_format en la misma llamada, así
que el bucle contesta en texto y, si quien llama lo pide, una llamada MÁS, sin tools y con el schema, convierte esa
respuesta en piezas. Se paga: una llamada con todo el historial (§ coste en el módulo).

La forma la garantiza el proveedor (strict); el contenido se valida aquí, como cualquier entrada externa (módulo 93).
"""

import logging
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, ValidationError

from asistente.application.ports.i_llm import ILLM
from asistente.application.prompts.estructura import ESTRUCTURA
from asistente.application.tools.esquema_json import esquema_json
from asistente.domain.exceptions.llm_exception import LLMException
from asistente.domain.read_models.respuesta_estructurada import Cifra, RespuestaEstructurada
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.peticion_llm import PeticionLLM
from asistente.domain.vo.respuesta_llm import RespuestaLLM

logger = logging.getLogger(__name__)
MAX_SEGUIMIENTO = 3


def _corto(texto: str) -> str:
    if not 0 < len(texto.strip()) <= 160:
        raise ValueError("vacío o de más de 160 caracteres")
    return texto.strip()


def _no_vacio(texto: str) -> str:
    if not texto.strip():
        raise ValueError("vacío")
    return texto


# Las longitudes, en validadores NUESTROS y no en el schema: el modo strict de Groq no admite todo JSON Schema
# (medido: con $defs y minLength/maxLength, json_validate_failed sin generación; sin ellos, pasa)
Corto = Annotated[str, AfterValidator(_corto)]


class _CifraJSON(BaseModel):
    model_config = ConfigDict(extra="forbid")
    concepto: Corto
    importe: Corto


class _RespuestaJSON(BaseModel):
    # Sin máximos en el schema: se comprueban aquí (el número de preguntas, al construir la respuesta)
    model_config = ConfigDict(extra="forbid")
    texto: Annotated[str, AfterValidator(_no_vacio)]
    cifras: list[_CifraJSON]
    seguimiento: list[Corto]


ESQUEMA = EsquemaRespuesta("respuesta_gastos", esquema_json(_RespuestaJSON))


def estructurar(llm: ILLM, mensajes: tuple[Mensaje, ...]) -> tuple[RespuestaEstructurada | None, RespuestaLLM | None]:
    """`mensajes` acaba con la respuesta del modelo. Si algo falla, (None, …): el texto sigue siendo la respuesta."""
    peticion = PeticionLLM(
        sistema=ESTRUCTURA.rellenar(max_seguimiento=MAX_SEGUIMIENTO), mensajes=mensajes, esquema=ESQUEMA
    )
    try:
        r = llm.generar(peticion)
    except LLMException:
        logger.warning("Sin respuesta estructurada: el LLM no está disponible", exc_info=True)
        return None, None
    try:
        datos = _RespuestaJSON.model_validate_json(r.texto)
    except ValidationError:
        logger.warning("Sin respuesta estructurada: JSON no válido (%s caracteres)", len(r.texto))
        return None, r
    return (
        RespuestaEstructurada(
            texto=datos.texto,
            cifras=tuple(Cifra(c.concepto, c.importe) for c in datos.cifras),
            seguimiento=tuple(datos.seguimiento[:MAX_SEGUIMIENTO]),
        ),
        r,
    )
