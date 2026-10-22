# notificaciones/application/obtener_estado_inicial_use_case/dtos/estado_inicial_output_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EstadoInicialOutputDTO:
    hogares: tuple[int, ...]  # los grupos de hogar del socket
    no_leidas: int
