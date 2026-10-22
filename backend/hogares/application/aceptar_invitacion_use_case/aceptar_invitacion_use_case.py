# hogares/application/aceptar_invitacion_use_case/aceptar_invitacion_use_case.py (módulos 71 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from hogares.application.aceptar_invitacion_use_case.dtos.aceptar_invitacion_input_dto import AceptarInvitacionInputDTO
from hogares.application.aceptar_invitacion_use_case.i_aceptar_invitacion_use_case import IAceptarInvitacionUseCase
from hogares.application.shared.dtos.membresia_output_dto import MembresiaOutputDTO
from hogares.domain.events.miembro_anadido_event import MiembroAnadidoEvent
from hogares.domain.exceptions.invitacion_no_valida_exception import InvitacionNoValidaException
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.domain.repositories.i_invitacion_command_repository import IInvitacionCommandRepository
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository


class AceptarInvitacionUseCase(IAceptarInvitacionUseCase):
    """Sin rol_minimo: quien acepta aún no es miembro. La regla es de la invitación (vigente, de su email)."""

    def __init__(
        self,
        *,
        invitaciones: IInvitacionCommandRepository,
        miembros: IMembresiaCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.invitaciones, self.miembros, self.eventos, self.uow, self.reloj = (
            invitaciones,
            miembros,
            eventos,
            uow,
            reloj,
        )

    def ejecutar(self, entrada: AceptarInvitacionInputDTO) -> MembresiaOutputDTO:
        with self.uow:
            invitacion = self.invitaciones.por_token(entrada.token)
            if invitacion is None:
                raise InvitacionNoValidaException()
            membresia = invitacion.aceptar(usuario_id=entrada.usuario_id, email=entrada.email, ahora=self.reloj.ahora())
            if self.miembros.es_miembro(invitacion.hogar_id, usuario_id=entrada.usuario_id):
                raise YaEsMiembroException()
            self.miembros.guardar(membresia)
            self.invitaciones.guardar(invitacion)
            self.eventos.publicar(MiembroAnadidoEvent(membresia.hogar_id, membresia.usuario_id, membresia.rol))
        return MembresiaOutputDTO.desde_bo(membresia)
