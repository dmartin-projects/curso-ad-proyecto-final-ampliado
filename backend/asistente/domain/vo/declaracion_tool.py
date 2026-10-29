# asistente/domain/vo/declaracion_tool.py — lo que el modelo VE de una tool (módulo 93)
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class DeclaracionTool:
    """Nombre, para qué sirve y el JSON Schema de sus argumentos. El modelo no ve el código: solo esto."""

    nombre: str
    descripcion: str
    parametros: dict[str, Any] = field(default_factory=lambda: {"type": "object", "properties": {}})
