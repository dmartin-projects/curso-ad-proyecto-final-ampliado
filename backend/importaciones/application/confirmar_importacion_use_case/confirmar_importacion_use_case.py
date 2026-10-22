# importaciones/application/confirmar_importacion_use_case/confirmar_importacion_use_case.py (módulos 75 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol
from importaciones.application.confirmar_importacion_use_case.dtos.confirmar_importacion_input_dto import (
    ConfirmarImportacionInputDTO,
)
from importaciones.application.confirmar_importacion_use_case.i_confirmar_importacion_use_case import (
    IConfirmarImportacionUseCase,
)
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO
from importaciones.domain.events.importacion_confirmada_event import ImportacionConfirmadaEvent
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository


class ConfirmarImportacionUseCase(IConfirmarImportacionUseCase):
    rol_minimo = Rol.MIEMBRO

    def __init__(
        self, *, importaciones: IImportacionCommandRepository, eventos: IPublicadorEventos, uow: IUnidadDeTrabajo
    ):
        self.importaciones, self.eventos, self.uow = importaciones, eventos, uow

    def ejecutar(self, entrada: ConfirmarImportacionInputDTO) -> ImportacionOutputDTO:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            importacion = self.importaciones.obtener(entrada.hogar_id, entrada.importacion_id, bloquear=True)
            importacion.confirmar()
            if entrada.separar:
                self.importaciones.separar(importacion.id, entrada.separar)
            filas = tuple(self.importaciones.filas_a_importar(importacion.id))
            self.importaciones.guardar(importacion)
            self.eventos.publicar(ImportacionConfirmadaEvent(importacion.id, filas))  # los lotes, al confirmar
        return ImportacionOutputDTO.desde_bo(importacion)
