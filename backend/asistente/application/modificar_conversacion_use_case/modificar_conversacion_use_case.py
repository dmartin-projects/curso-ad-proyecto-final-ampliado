# asistente/application/modificar_conversacion_use_case/modificar_conversacion_use_case.py (módulo 97)
from asistente.application.modificar_conversacion_use_case.dtos.modificar_conversacion_input_dto import (
    ModificarConversacionInputDTO,
)
from asistente.application.modificar_conversacion_use_case.i_modificar_conversacion_use_case import (
    IModificarConversacionUseCase,
)
from asistente.application.shared.dtos.conversacion_output_dto import ConversacionOutputDTO
from asistente.domain.repositories.i_carpeta_command_repository import ICarpetaCommandRepository
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol

EDITABLES = frozenset({"titulo", "carpeta_id"})


class ModificarConversacionUseCase(IModificarConversacionUseCase):
    rol_minimo = Rol.LECTOR

    def __init__(
        self,
        *,
        conversaciones: IConversacionCommandRepository,
        carpetas: ICarpetaCommandRepository,
        uow: IUnidadDeTrabajo,
    ):
        self.conversaciones, self.carpetas, self.uow = conversaciones, carpetas, uow

    def ejecutar(self, entrada: ModificarConversacionInputDTO) -> ConversacionOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        if desconocidos := entrada.cambios.keys() - EDITABLES:
            raise TypeError(f"No se pueden modificar: {sorted(desconocidos)}")
        usuario_id = entrada.actor.usuario_id
        with self.uow:
            conversacion = self.conversaciones.obtener(usuario_id, entrada.hogar_id, entrada.conversacion_id)
            if "titulo" in entrada.cambios:
                conversacion.renombrar(entrada.cambios["titulo"])
            if "carpeta_id" in entrada.cambios:
                carpeta_id = entrada.cambios["carpeta_id"]
                if carpeta_id is not None:  # una carpeta suya en este hogar, o un 404
                    self.carpetas.obtener(usuario_id, entrada.hogar_id, carpeta_id)
                conversacion.mover_a(carpeta_id)
            self.conversaciones.guardar(conversacion)
        return ConversacionOutputDTO.desde_bo(conversacion)
