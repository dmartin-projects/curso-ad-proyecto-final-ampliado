# asistente/application/shared/dtos/mensaje_output_dto.py (módulo 97)
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True, slots=True)
class MensajeOutputDTO:
    id: int
    rol: str
    texto: str
    datos: dict[str, Any]  # gráficos, archivos (con su URL de descarga), propuestas (con su estado), seguimiento…
    incompleto: bool
    nombre_adjunto: str
    creado: datetime
