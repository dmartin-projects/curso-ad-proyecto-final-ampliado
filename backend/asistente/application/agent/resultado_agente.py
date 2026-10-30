# asistente/application/agent/resultado_agente.py — lo que devuelve el agente al contestar una pregunta (módulos 94, 96, 97 y 102)
from dataclasses import dataclass

from asistente.domain.enums.motivo_parada import MotivoParada
from asistente.domain.read_models.respuesta_estructurada import RespuestaEstructurada
from asistente.domain.vo.artefacto import Artefacto
from asistente.domain.vo.llamada_tool import LlamadaTool
from asistente.domain.vo.mensaje import Mensaje
from asistente.domain.vo.uso import Uso


@dataclass(frozen=True, slots=True)
class ResultadoAgente:
    texto: str  # lo que se enseña al usuario
    nuevos: tuple[Mensaje, ...]  # lo que se AÑADE a la conversación: turnos del modelo y resultados de tools
    motivo: MotivoParada
    uso: Uso  # la suma de todas las vueltas
    iteraciones: int  # llamadas al LLM
    llamadas: tuple[LlamadaTool, ...]  # todas las tool calls que pidió (ejecutadas o rechazadas)
    modelos: tuple[str, ...]  # el que respondió en cada vuelta (con reserva, puede cambiar a mitad)
    duracion_ms: int
    estructurada: RespuestaEstructurada | None = None  # módulo 96: solo si se pidió (y salió bien)
    artefactos: tuple[Artefacto, ...] = ()  # módulo 97: gráficos, archivos y propuestas, en el orden en que salieron
    terceros: bool = False  # módulo 102: el modelo ha leído texto de terceros (la conversación queda marcada)
