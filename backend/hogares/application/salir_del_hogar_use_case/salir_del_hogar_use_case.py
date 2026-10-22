# hogares/application/salir_del_hogar_use_case/salir_del_hogar_use_case.py — irse de un hogar (ejercicio 1 del módulo 88)
from core.application.ports.i_auditoria import IAuditoria
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.accion import Accion
from core.domain.enums.rol import Rol
from hogares.application.salir_del_hogar_use_case.dtos.salir_del_hogar_input_dto import SalirDelHogarInputDTO
from hogares.application.salir_del_hogar_use_case.i_salir_del_hogar_use_case import ISalirDelHogarUseCase
from hogares.domain.events.miembro_expulsado_event import MiembroExpulsadoEvent
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from hogares.domain.services.administradores import exigir_otro_admin


class SalirDelHogarUseCase(ISalirDelHogarUseCase):
    """Irse de un hogar, con cualquier rol. La regla del último administrador es la misma que al expulsar: la decide
    el dominio (exigir_otro_admin), no quien llama. Se audita, como expulsar."""

    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        miembros: IMembresiaCommandRepository,
        auditoria: IAuditoria,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.miembros, self.auditoria, self.eventos, self.uow = miembros, auditoria, eventos, uow

    def ejecutar(self, entrada: SalirDelHogarInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            membresia = self.miembros.del_usuario(entrada.hogar_id, entrada.actor.usuario_id, bloquear=True)
            exigir_otro_admin(membresia, self.miembros.admins(entrada.hogar_id))
            self.miembros.eliminar(membresia)
            self.auditoria.registrar(Accion.BORRAR, membresia, entrada.actor.usuario_id)
            self.eventos.publicar(MiembroExpulsadoEvent(entrada.hogar_id, membresia.usuario_id))
