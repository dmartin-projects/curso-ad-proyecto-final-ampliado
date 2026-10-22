# hogares/application/eliminar_hogar_use_case/eliminar_hogar_use_case.py (módulo 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from hogares.application.eliminar_hogar_use_case.dtos.eliminar_hogar_input_dto import EliminarHogarInputDTO
from hogares.application.eliminar_hogar_use_case.i_eliminar_hogar_use_case import IEliminarHogarUseCase
from hogares.domain.repositories.i_hogar_command_repository import IHogarCommandRepository
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository


class EliminarHogarUseCase(IEliminarHogarUseCase):
    """Con todo lo suyo. Lo que borra la base de datos en cascada (movimientos, membresías) no pasa por ningún use
    case: sus mensajes al outbox y sus avisos los ponen los receivers de cascada (eventos y notificaciones)."""

    rol_minimo = Rol.ADMIN

    def __init__(
        self,
        *,
        hogares: IHogarCommandRepository,
        miembros: IMembresiaCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.hogares, self.miembros, self.eventos, self.uow = hogares, miembros, eventos, uow

    def ejecutar(self, entrada: EliminarHogarInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            self.hogares.eliminar(self.hogares.obtener(entrada.hogar_id))
