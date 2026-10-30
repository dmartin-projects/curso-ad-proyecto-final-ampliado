# asistente/domain/vo/mensaje_de_conversacion.py — un mensaje del historial, con lo que necesita la interfaz (módulo 97)
from dataclasses import dataclass, field
from typing import Any

from asistente.domain.vo.mensaje import Mensaje


@dataclass(frozen=True, slots=True)
class MensajeDeConversacion:
    """Lo que se guarda por cada Mensaje del agente.

    `mensaje` es lo que se reenvía al modelo en la pregunta siguiente; lo demás es para la interfaz. Por eso son dos
    textos: la pregunta con un adjunto viaja con el texto del OCR dentro (`mensaje.texto`), pero en el chat se ve lo
    que escribió la persona (`texto`). Solo son `visibles` las preguntas y las respuestas finales: los turnos con
    tool calls y sus resultados se guardan (el historial tiene que ser el mismo) pero no se pintan.
    """

    mensaje: Mensaje
    visible: bool = False
    texto: str = ""  # lo que se enseña (si es visible)
    datos: dict[str, Any] = field(default_factory=dict)  # gráficos, archivos, propuestas, seguimiento, uso…
    adjunto: str | None = None  # la ruta del archivo adjunto, en el almacenamiento
    nombre_adjunto: str = ""
