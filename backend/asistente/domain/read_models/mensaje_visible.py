# asistente/domain/read_models/mensaje_visible.py — un mensaje tal como se pinta en el chat (módulo 97)
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class MensajeVisible:
    id: int
    rol: str  # "usuario" | "modelo"
    texto: str
    datos: dict[str, Any]  # gráficos, archivos, propuestas, seguimiento…
    incompleto: bool  # una pregunta cancelada o que falló: se ve, pero no se reenvía al modelo
    nombre_adjunto: str
    creado: datetime
