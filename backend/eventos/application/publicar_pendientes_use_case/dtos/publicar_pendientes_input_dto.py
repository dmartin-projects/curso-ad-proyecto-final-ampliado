# eventos/application/publicar_pendientes_use_case/dtos/publicar_pendientes_input_dto.py (módulos 85 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class PublicarPendientesInputDTO:
    tamano: int = 500
