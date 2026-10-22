# importaciones/application/finalizar_importacion_use_case/finalizar_importacion_use_case.py (módulos 75 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from importaciones.application.finalizar_importacion_use_case.dtos.finalizar_importacion_input_dto import (
    FinalizarImportacionInputDTO,
)
from importaciones.application.finalizar_importacion_use_case.i_finalizar_importacion_use_case import (
    IFinalizarImportacionUseCase,
)
from importaciones.application.shared.dtos.importacion_output_dto import ImportacionOutputDTO
from importaciones.domain.enums.estado_importacion import E
from importaciones.domain.events.importacion_terminada_event import ImportacionTerminadaEvent
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository


class FinalizarImportacionUseCase(IFinalizarImportacionUseCase):
    """El cierre del chord: cuando han terminado TODOS los lotes."""

    def __init__(
        self,
        *,
        importaciones: IImportacionCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.importaciones, self.eventos, self.uow, self.reloj = importaciones, eventos, uow, reloj

    def ejecutar(self, entrada: FinalizarImportacionInputDTO) -> ImportacionOutputDTO:
        importacion_id = entrada.importacion_id
        with self.uow:
            importacion = self.importaciones.por_id(importacion_id, bloquear=True)
            if importacion.estado != E.IMPORTANDO:
                return ImportacionOutputDTO.desde_bo(importacion)  # entrega duplicada del cierre
            importacion.completar(self.reloj.ahora())
            self.importaciones.guardar(importacion)
            self.eventos.publicar(
                ImportacionTerminadaEvent(
                    importacion_id, str(importacion.formato), completada=True, creados=importacion.creados
                )
            )
        return ImportacionOutputDTO.desde_bo(importacion)
