# backoffice/application/obtener_registro_auditoria_use_case/obtener_registro_auditoria_use_case.py (módulo 88)
from backoffice.application.obtener_registro_auditoria_use_case.dtos.obtener_registro_auditoria_input_dto import (
    ObtenerRegistroAuditoriaInputDTO,
)
from backoffice.application.obtener_registro_auditoria_use_case.i_obtener_registro_auditoria_use_case import (
    IObtenerRegistroAuditoriaUseCase,
)
from backoffice.application.shared.dtos.registro_auditoria_soporte_output_dto import RegistroAuditoriaSoporteOutputDTO
from backoffice.domain.repositories.i_auditoria_soporte_query_service import IAuditoriaSoporteQueryService


class ObtenerRegistroAuditoriaUseCase(IObtenerRegistroAuditoriaUseCase):
    """Sin rol que exigir: el backoffice es solo para el personal, y eso (y sus permisos de Django) lo comprueba el
    adapter de entrada. Lee de TODOS los hogares."""

    def __init__(self, *, auditoria: IAuditoriaSoporteQueryService):
        self.auditoria = auditoria

    def ejecutar(self, entrada: ObtenerRegistroAuditoriaInputDTO) -> RegistroAuditoriaSoporteOutputDTO | None:
        leido = self.auditoria.detalle(entrada.registro_id)
        return None if leido is None else RegistroAuditoriaSoporteOutputDTO.desde_read_model(leido)
