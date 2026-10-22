# hogares/application/cambiar_rol_use_case/cambiar_rol_use_case.py (módulos 71 y 88)
from dataclasses import replace

from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from hogares.application.cambiar_rol_use_case.dtos.cambiar_rol_input_dto import CambiarRolInputDTO
from hogares.application.cambiar_rol_use_case.i_cambiar_rol_use_case import ICambiarRolUseCase
from hogares.application.shared.dtos.membresia_output_dto import MembresiaOutputDTO
from hogares.domain.events.rol_cambiado_event import RolCambiadoEvent
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from hogares.domain.services.administradores import exigir_otro_admin


class CambiarRolUseCase(ICambiarRolUseCase):
    """Se audita: quién cambió el rol de quién (ejercicio 3 del módulo 88)."""

    rol_minimo = Rol.ADMIN

    def __init__(
        self,
        *,
        miembros: IMembresiaCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.miembros, self.auditoria, self.eventos, self.uow = miembros, auditoria, eventos, uow

    def ejecutar(self, entrada: CambiarRolInputDTO) -> MembresiaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            membresia = self.miembros.obtener(entrada.hogar_id, entrada.membresia_id, bloquear=True)
            if Rol(entrada.rol) != Rol.ADMIN:
                exigir_otro_admin(membresia, self.miembros.admins(entrada.hogar_id))
            antes = replace(membresia)
            membresia.rol = Rol(entrada.rol)
            self.miembros.guardar(membresia)
            self.auditoria.registrar(Accion.MODIFICAR, membresia, entrada.actor.usuario_id, antes=antes)
            self.eventos.publicar(RolCambiadoEvent(entrada.hogar_id, membresia.usuario_id, membresia.rol))
        return MembresiaOutputDTO.desde_bo(membresia)
