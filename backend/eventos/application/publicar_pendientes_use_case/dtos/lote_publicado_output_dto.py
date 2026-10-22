# eventos/application/publicar_pendientes_use_case/dtos/lote_publicado_output_dto.py (módulos 85 y 88)
from dataclasses import dataclass
from datetime import datetime

from eventos.application.publicar_pendientes_use_case.dtos.evento_publicado_output_dto import (
    EventoPublicadoOutputDTO,
)


@dataclass(frozen=True, slots=True)
class LotePublicadoOutputDTO:
    eventos: tuple[EventoPublicadoOutputDTO, ...]
    cuando: datetime | None  # None: no había nada que publicar
