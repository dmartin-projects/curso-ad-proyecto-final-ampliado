# hogares/application/obtener_invitacion_use_case/obtener_invitacion_use_case.py (módulo 88)
from core.domain.enums.rol import Rol
from hogares.application.obtener_invitacion_use_case.dtos.invitacion_listada_output_dto import (
    InvitacionListadaOutputDTO,
)
from hogares.application.obtener_invitacion_use_case.dtos.obtener_invitacion_input_dto import ObtenerInvitacionInputDTO
from hogares.application.obtener_invitacion_use_case.i_obtener_invitacion_use_case import IObtenerInvitacionUseCase
from hogares.domain.repositories.i_invitacion_query_service import IInvitacionQueryService


class ObtenerInvitacionUseCase(IObtenerInvitacionUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, invitaciones: IInvitacionQueryService):
        self.invitaciones = invitaciones

    def ejecutar(self, entrada: ObtenerInvitacionInputDTO) -> InvitacionListadaOutputDTO | None:
        entrada.actor.exigir(self.rol_minimo)
        leida = self.invitaciones.detalle(entrada.hogar_id, entrada.invitacion_id)
        return None if leida is None else InvitacionListadaOutputDTO.desde_read_model(leida)
