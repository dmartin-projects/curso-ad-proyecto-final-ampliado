# backoffice/application/listar_auditoria_use_case/listar_auditoria_use_case.py (módulo 88)
from backoffice.application.listar_auditoria_use_case.dtos.listar_auditoria_input_dto import ListarAuditoriaInputDTO
from backoffice.application.listar_auditoria_use_case.i_listar_auditoria_use_case import IListarAuditoriaUseCase
from backoffice.application.shared.dtos.registro_auditoria_soporte_output_dto import RegistroAuditoriaSoporteOutputDTO
from backoffice.domain.repositories.i_auditoria_soporte_query_service import IAuditoriaSoporteQueryService
from core.application.dtos.pagina_output_dto import PaginaOutputDTO


class ListarAuditoriaUseCase(IListarAuditoriaUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, auditoria: IAuditoriaSoporteQueryService):
        self.auditoria = auditoria

    def ejecutar(self, entrada: ListarAuditoriaInputDTO) -> PaginaOutputDTO[RegistroAuditoriaSoporteOutputDTO]:
        pagina = self.auditoria.listar(entrada.query, modelo=entrada.modelo)
        return PaginaOutputDTO.desde_pagina(pagina, RegistroAuditoriaSoporteOutputDTO.desde_read_model)
