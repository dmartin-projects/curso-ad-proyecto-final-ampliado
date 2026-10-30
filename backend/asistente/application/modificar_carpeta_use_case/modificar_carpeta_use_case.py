# asistente/application/modificar_carpeta_use_case/modificar_carpeta_use_case.py (módulo 97, ejercicio 1)
from asistente.application.modificar_carpeta_use_case.dtos.modificar_carpeta_input_dto import ModificarCarpetaInputDTO
from asistente.application.modificar_carpeta_use_case.i_modificar_carpeta_use_case import IModificarCarpetaUseCase
from asistente.application.shared.dtos.carpeta_output_dto import CarpetaOutputDTO
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class ModificarCarpetaUseCase(IModificarCarpetaUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(self, *, carpetas: ICarpetaCommandRepository, uow: IUnidadDeTrabajo):
        self.carpetas, self.uow = carpetas, uow

    def ejecutar(self, entrada: ModificarCarpetaInputDTO) -> CarpetaOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            carpeta = self.carpetas.obtener(entrada.actor.usuario_id, entrada.hogar_id, entrada.carpeta_id)
            carpeta.renombrar(entrada.nombre)
            self.carpetas.guardar(carpeta)  # el nombre repetido lo dice la constraint (CarpetaRepetidaException)
        return CarpetaOutputDTO.desde_bo(carpeta)
