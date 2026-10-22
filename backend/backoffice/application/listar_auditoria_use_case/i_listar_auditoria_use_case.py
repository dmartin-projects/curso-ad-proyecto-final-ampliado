# backoffice/application/listar_auditoria_use_case/i_listar_auditoria_use_case.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.application.listar_auditoria_use_case.dtos.listar_auditoria_input_dto import ListarAuditoriaInputDTO
from backoffice.application.shared.dtos.registro_auditoria_soporte_output_dto import RegistroAuditoriaSoporteOutputDTO
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class IListarAuditoriaUseCase(ABC):
    @abstractmethod
    def ejecutar(self, entrada: ListarAuditoriaInputDTO) -> PaginaOutputDTO[RegistroAuditoriaSoporteOutputDTO]: ...
