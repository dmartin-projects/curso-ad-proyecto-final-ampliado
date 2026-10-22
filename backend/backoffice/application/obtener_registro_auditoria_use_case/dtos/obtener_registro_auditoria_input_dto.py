# backoffice/application/obtener_registro_auditoria_use_case/dtos/obtener_registro_auditoria_input_dto.py (módulo 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class ObtenerRegistroAuditoriaInputDTO:
    registro_id: int
