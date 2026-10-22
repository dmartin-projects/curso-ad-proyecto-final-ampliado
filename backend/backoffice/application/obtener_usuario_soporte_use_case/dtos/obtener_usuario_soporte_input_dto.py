# backoffice/application/obtener_usuario_soporte_use_case/dtos/obtener_usuario_soporte_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerUsuarioSoporteInputDTO:
    usuario_id: int
