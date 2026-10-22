# backoffice/application/obtener_registro_auditoria_use_case/i_obtener_registro_auditoria_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.obtener_registro_auditoria_use_case.dtos.obtener_registro_auditoria_input_dto import (
    ObtenerRegistroAuditoriaInputDTO,
)
from backoffice.application.shared.dtos.registro_auditoria_soporte_output_dto import RegistroAuditoriaSoporteOutputDTO


class IObtenerRegistroAuditoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ObtenerRegistroAuditoriaInputDTO) -> RegistroAuditoriaSoporteOutputDTO | None: ...
