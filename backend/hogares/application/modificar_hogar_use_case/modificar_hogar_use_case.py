# hogares/application/modificar_hogar_use_case/modificar_hogar_use_case.py (módulo 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from hogares.application.modificar_hogar_use_case.dtos.modificar_hogar_input_dto import ModificarHogarInputDTO
from hogares.application.modificar_hogar_use_case.i_modificar_hogar_use_case import IModificarHogarUseCase
from hogares.application.shared.dtos.hogar_output_dto import HogarOutputDTO
from hogares.domain.repositories.i_hogar_command_repository import IHogarCommandRepository
from hogares.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository


class ModificarHogarUseCase(IModificarHogarUseCase):
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

    def ejecutar(self, entrada: ModificarHogarInputDTO) -> HogarOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            hogar = self.hogares.obtener(entrada.hogar_id)
            hogar.modificar(**entrada.cambios)
            self.hogares.guardar(hogar)
        return HogarOutputDTO.desde_bo(hogar)
