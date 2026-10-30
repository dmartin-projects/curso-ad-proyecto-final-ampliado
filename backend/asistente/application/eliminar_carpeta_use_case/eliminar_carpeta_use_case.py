# asistente/application/eliminar_carpeta_use_case/eliminar_carpeta_use_case.py (módulo 97)
from asistente.application.eliminar_carpeta_use_case.dtos.eliminar_carpeta_input_dto import EliminarCarpetaInputDTO
from asistente.application.eliminar_carpeta_use_case.i_eliminar_carpeta_use_case import IEliminarCarpetaUseCase
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class EliminarCarpetaUseCase(IEliminarCarpetaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, carpetas: ICarpetaCommandRepository, uow: IUnidadDeTrabajo):
        self.carpetas, self.uow = carpetas, uow

    def ejecutar(self, entrada: EliminarCarpetaInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            carpeta = self.carpetas.obtener(entrada.actor.usuario_id, entrada.hogar_id, entrada.carpeta_id)
            self.carpetas.eliminar(carpeta)
