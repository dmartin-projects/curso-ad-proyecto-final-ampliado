# asistente/domain/vo/respuesta_llm.py — un turno del modelo, con lo que ha costado (módulo 93)
from dataclasses import dataclass, field

from asistente.domain.enums.motivo_fin import MotivoFin
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso


@dataclass(frozen=True, slots=True)
class RespuestaLLM:
    mensaje: Mensaje  # rol MODELO: se añade tal cual al historial
    motivo: MotivoFin
    uso: Uso = field(default_factory=Uso)
    modelo: str = ""  # el que ha respondido de verdad (con reserva, módulo 94, puede no ser el principal)
    duracion_ms: int = 0
    # El razonamiento del modelo, si el proveedor lo devuelve. Para depurar: no es para el usuario (puede contener
    # datos de las tools tal cual, o ideas descartadas) y no se reenvía en el siguiente turno.
    razonamiento: str = ""

    @property
    def texto(self) -> str:
        return self.mensaje.texto

    @property
    def llamadas(self) -> tuple[LlamadaTool, ...]:
        return self.mensaje.llamadas
