# hogares/application/expulsar_miembro_use_case/expulsar_miembro_use_case.py (módulos 71 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from hogares.application.expulsar_miembro_use_case.dtos.expulsar_miembro_input_dto import ExpulsarMiembroInputDTO
from hogares.application.expulsar_miembro_use_case.i_expulsar_miembro_use_case import IExpulsarMiembroUseCase
from hogares.domain.events.miembro_expulsado_event import MiembroExpulsadoEvent
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from hogares.domain.services.administradores import exigir_otro_admin


class ExpulsarMiembroUseCase(IExpulsarMiembroUseCase):
    """Sacar a alguien del hogar. El último administrador no puede irse: el hogar se quedaría sin nadie que pudiera
    gestionarlo (la misma regla que al cambiar de rol: exigir_otro_admin)."""

    rol_minimo = Rol.ADMIN

    def __init__(self, *, miembros: IMembresiaCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo):
        self.miembros, self.eventos, self.uow = miembros, eventos, uow

    def ejecutar(self, entrada: ExpulsarMiembroInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            membresia = self.miembros.obtener(entrada.hogar_id, entrada.membresia_id, bloquear=True)
            exigir_otro_admin(membresia, self.miembros.admins(entrada.hogar_id))
            self.miembros.eliminar(membresia)
            self.eventos.publicar(MiembroExpulsadoEvent(entrada.hogar_id, membresia.usuario_id))
