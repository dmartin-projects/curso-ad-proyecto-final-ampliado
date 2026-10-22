# hogares/application/crear_hogar_use_case/crear_hogar_use_case.py (módulos 71 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from hogares.application.crear_hogar_use_case.dtos.crear_hogar_input_dto import CrearHogarInputDTO
from hogares.application.crear_hogar_use_case.i_crear_hogar_use_case import ICrearHogarUseCase
from hogares.application.shared.dtos.hogar_output_dto import HogarOutputDTO
from hogares.domain.bo.hogar import Hogar
from hogares.domain.bo.membresia import Membresia
from hogares.domain.events.hogar_creado_event import HogarCreadoEvent
from hogares.domain.events.miembro_anadido_event import MiembroAnadidoEvent
from hogares.domain.repositories.i_hogar_command_repository import IHogarCommandRepository
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository


class CrearHogarUseCase(ICrearHogarUseCase):
    """Sin rol_minimo: quien crea un hogar aún no tiene rol en él. Será su administrador."""

    def __init__(
        self,
        *,
        hogares: IHogarCommandRepository,
        miembros: IMembresiaCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
    ):
        self.hogares, self.miembros, self.eventos, self.uow = hogares, miembros, eventos, uow

    def ejecutar(self, entrada: CrearHogarInputDTO) -> HogarOutputDTO:
        hogar = Hogar(nombre=entrada.nombre, moneda=entrada.moneda, zona_horaria=entrada.zona_horaria)
        with self.uow:
            self.hogares.guardar(hogar)
            admin = Membresia(hogar_id=hogar.id, usuario_id=entrada.usuario_id, rol=Rol.ADMIN)
            self.miembros.guardar(admin)
            # finanzas crea las categorías por defecto (módulo 72) DENTRO de esta transacción: nunca hay un hogar
            # sin sus categorías
            self.eventos.publicar(
                HogarCreadoEvent(hogar.id), MiembroAnadidoEvent(hogar.id, entrada.usuario_id, Rol.ADMIN)
            )
        return HogarOutputDTO.desde_bo(hogar)
