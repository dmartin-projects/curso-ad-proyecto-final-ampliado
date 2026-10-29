# asistente/domain/vo/esquema_respuesta.py — structured output: la respuesta, un JSON con este schema (módulo 93)
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class EsquemaRespuesta:
    """Pedir JSON que cumpla un JSON Schema, y que el proveedor lo GARANTICE (estricto) o lo intente.

    La forma está garantizada; el contenido, no: un importe de 0 € o una fecha del futuro cumplen el schema. La
    salida de un LLM se valida como cualquier entrada externa (ejercicio 1).
    """

    nombre: str  # lo exige la API (response_format.json_schema.name): letras, números, _ y -
    esquema: dict[str, Any]
    estricto: bool = True  # constrained decoding: el modelo no PUEDE generar algo que no cumpla el schema
