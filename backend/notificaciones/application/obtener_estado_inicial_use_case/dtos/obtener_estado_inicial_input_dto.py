# notificaciones/application/obtener_estado_inicial_use_case/dtos/obtener_estado_inicial_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerEstadoInicialInputDTO:
    usuario_id: int
