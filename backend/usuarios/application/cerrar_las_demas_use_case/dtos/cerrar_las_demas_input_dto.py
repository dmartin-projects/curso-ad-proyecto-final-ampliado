# usuarios/application/cerrar_las_demas_use_case/dtos/cerrar_las_demas_input_dto.py (módulo 92)
from dataclasses import dataclass


@dataclass(frozen=True)
class CerrarLasDemasInputDTO:
    usuario_id: int
    sid: str  # la de esta petición: se queda abierta
