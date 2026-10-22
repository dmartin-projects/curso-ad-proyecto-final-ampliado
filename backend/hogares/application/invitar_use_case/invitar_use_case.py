# hogares/application/invitar_use_case/invitar_use_case.py (módulos 71 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from hogares.application.invitar_use_case.dtos.invitacion_output_dto import InvitacionOutputDTO
from hogares.application.invitar_use_case.dtos.invitar_input_dto import InvitarInputDTO
from hogares.application.invitar_use_case.i_invitar_use_case import IInvitarUseCase
from hogares.domain.bo.invitacion import Invitacion, normalizar_email
from hogares.domain.events.invitacion_enviada_event import InvitacionEnviadaEvent
from hogares.domain.exceptions.ya_es_miembro_exception import YaEsMiembroException
from hogares.domain.repositories.i_invitacion_command_repository import IInvitacionCommandRepository
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository


class InvitarUseCase(IInvitarUseCase):
    rol_minimo = Rol.ADMIN

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

    def ejecutar(self, entrada: InvitarInputDTO) -> InvitacionOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        email = normalizar_email(entrada.email)
        with self.uow:
            if self.miembros.es_miembro(entrada.hogar_id, email=email):
                raise YaEsMiembroException()
            invitacion = self.invitaciones.pendiente(entrada.hogar_id, email)
            if invitacion is None:
                invitacion = Invitacion.nueva(
                    hogar_id=entrada.hogar_id,
                    email=email,
                    rol=entrada.rol,
                    invitado_por_id=entrada.actor.usuario_id,
                    ahora=self.reloj.ahora(),
                )
            else:  # invitar otra vez: la misma invitación (mismo enlace), con el rol nuevo y otros siete días
                invitacion.renovar(rol=entrada.rol, invitado_por_id=entrada.actor.usuario_id, ahora=self.reloj.ahora())
            self.invitaciones.guardar(invitacion)
            self.eventos.publicar(InvitacionEnviadaEvent(invitacion.id))
        return InvitacionOutputDTO.desde_bo(invitacion)
