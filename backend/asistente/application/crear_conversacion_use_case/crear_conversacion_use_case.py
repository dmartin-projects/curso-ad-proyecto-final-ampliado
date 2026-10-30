# asistente/application/crear_conversacion_use_case/crear_conversacion_use_case.py (módulo 97)
from asistente.application.crear_conversacion_use_case.dtos.crear_conversacion_input_dto import (
    CrearConversacionInputDTO,
)
from asistente.application.crear_conversacion_use_case.i_crear_conversacion_use_case import ICrearConversacionUseCase
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO
from asistente.domain.bo.conversacion import Conversacion
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol


class CrearConversacionUseCase(ICrearConversacionUseCase):
    # Cualquier miembro, también un lector: el asistente solo lee. Lo que cambia algo (una propuesta) lo decide, al
    # confirmarla, el use case de la app dueña con el rol de verdad.
    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        conversaciones: IConversacionCommandRepository,
        carpetas: ICarpetaCommandRepository,
        uow: IUnidadDeTrabajo,
    ):
        self.conversaciones, self.carpetas, self.uow = conversaciones, carpetas, uow

    def ejecutar(self, entrada: CrearConversacionInputDTO) -> ConversacionOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        usuario_id = entrada.actor.usuario_id
        with self.uow:
            if entrada.carpeta_id is not None:  # suya y de este hogar, o un 404
                self.carpetas.obtener(usuario_id, entrada.hogar_id, entrada.carpeta_id)
            conversacion = Conversacion(usuario_id, entrada.hogar_id, carpeta_id=entrada.carpeta_id)
            self.conversaciones.guardar(conversacion)
        return ConversacionOutputDTO.desde_bo(conversacion)
