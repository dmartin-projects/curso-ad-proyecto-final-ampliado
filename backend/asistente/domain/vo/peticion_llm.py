# asistente/domain/vo/peticion_llm.py — todo lo que viaja en UNA llamada al LLM (módulo 93)
from dataclasses import dataclass

from asistente.domain.enums.esfuerzo_de_razonamiento import EsfuerzoDeRazonamiento
from asistente.domain.vo.declaracion_tool import DeclaracionTool
from asistente.domain.vo.esquema_respuesta import EsquemaRespuesta
from asistente.domain.vo.mensaje import Mensaje


@dataclass(frozen=True, slots=True)
class PeticionLLM:
    """Un LLM es stateless: las instrucciones, el historial COMPLETO y las tools viajan en cada petición."""

    sistema: str  # las instrucciones (system prompt)
    mensajes: tuple[Mensaje, ...]
    tools: tuple[DeclaracionTool, ...] = ()
    usar_tools: bool = True  # False: el modelo VE las tools pero no puede llamarlas (la última vuelta, módulo 94)
    esquema: EsquemaRespuesta | None = None  # structured output
    temperatura: float | None = None  # None: la del proveedor
    esfuerzo: EsfuerzoDeRazonamiento | None = None  # None: lo que decida el proveedor
    max_tokens: int | None = None  # tope de la SALIDA (razonamiento incluido)

    def __post_init__(self):
        if not self.mensajes:
            raise ValueError("Una petición necesita al menos un mensaje.")
        if self.temperatura is not None and not 0 <= self.temperatura <= 2:
            raise ValueError("La temperatura va de 0 a 2.")
        if self.max_tokens is not None and self.max_tokens < 1:
            raise ValueError("max_tokens tiene que ser positivo.")
