# usuarios/application/listar_sesiones_use_case/dtos/listar_sesiones_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class ListarSesionesInputDTO:
    usuario_id: int
    sid_actual: str | None  # la de la petición: sale marcada como `actual`
