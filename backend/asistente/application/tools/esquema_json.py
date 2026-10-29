# asistente/application/tools/esquema_json.py — el JSON Schema de unos argumentos, limpio para un LLM (módulo 94)
from typing import Any

from pydantic import BaseModel


def esquema_json(modelo: type[BaseModel]) -> dict[str, Any]:
    """El JSON Schema de pydantic, en la forma más simple que entienden todos los modelos:

    - sin los "title" (repiten el nombre del campo) ni la descripción de la clase: se pagan en cada llamada;
    - un opcional (`X | None = None`) como `X` fuera de `required`, no como anyOf [X, null] con default null. Es lo
      mismo para el validador, pero no para un modelo: con el anyOf, qwen3.8-27b mandó mes=null en 1 de 5 llamadas
      sueltas y en todas las de dos preguntas seguidas del agente; con el string, en ninguna. Si un modelo manda null
      igual, pydantic lo acepta: el opcional sigue siéndolo.
    """
    esquema = _limpiar(modelo.model_json_schema())
    esquema.pop("description", None)
    return esquema


def _limpiar(nodo: Any) -> Any:
    if isinstance(nodo, list):
        return [_limpiar(x) for x in nodo]
    if not isinstance(nodo, dict):
        return nodo
    nodo = {k: _limpiar(v) for k, v in nodo.items() if k != "title"}
    opciones = nodo.get("anyOf")
    if opciones and len(opciones) == 2 and {"type": "null"} in opciones:
        (tipo,) = [o for o in opciones if o != {"type": "null"}]
        nodo = {**{k: v for k, v in nodo.items() if k != "anyOf"}, **tipo}
        if "default" in nodo and nodo["default"] is None:
            del nodo["default"]
    return nodo
