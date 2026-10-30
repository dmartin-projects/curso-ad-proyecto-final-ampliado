# asistente/application/crear_carpeta_use_case/crear_carpeta_use_case.py (módulo 97)
from asistente.application.crear_carpeta_use_case.dtos.crear_carpeta_input_dto import CrearCarpetaInputDTO
from asistente.application.crear_carpeta_use_case.i_crear_carpeta_use_case import ICrearCarpetaUseCase
from asistente.application.shared.dtos.carpeta_output_dto import CarpetaOutputDTO
from asistente.domain.bo.carpeta import Carpeta
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class CrearCarpetaUseCase(ICrearCarpetaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, carpetas: ICarpetaCommandRepository, uow: IUnidadDeTrabajo):
        self.carpetas, self.uow = carpetas, uow

    def ejecutar(self, entrada: CrearCarpetaInputDTO) -> CarpetaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        carpeta = Carpeta(entrada.actor.usuario_id, entrada.hogar_id, entrada.nombre)
        with self.uow:
            self.carpetas.guardar(carpeta)  # CarpetaRepetidaException si ya tiene una con ese nombre
        return CarpetaOutputDTO.desde_bo(carpeta)
