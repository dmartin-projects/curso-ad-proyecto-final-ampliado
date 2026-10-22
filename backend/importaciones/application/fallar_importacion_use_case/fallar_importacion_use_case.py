# importaciones/application/fallar_importacion_use_case/fallar_importacion_use_case.py (módulos 75 y 88)
from core.application.ports.i_publicador_eventos import IPublicadorEventos
from core.application.ports.i_reloj import IReloj
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from importaciones.application.fallar_importacion_use_case.dtos.fallar_importacion_input_dto import (
    FallarImportacionInputDTO,
)
from importaciones.application.fallar_importacion_use_case.i_fallar_importacion_use_case import (
    IFallarImportacionUseCase,
)
from importaciones.domain.events.importacion_terminada_event import ImportacionTerminadaEvent
from importaciones.domain.repositories.i_importacion_command_repository import IImportacionCommandRepository


class FallarImportacionUseCase(IFallarImportacionUseCase):
    """A error, si aún podía fallar. Lo piden las tareas (y AnalizarExtractoUseCase, si el archivo no se puede leer)."""

    def __init__(
        self,
        *,
        importaciones: IImportacionCommandRepository,
        eventos: IPublicadorEventos,
        uow: IUnidadDeTrabajo,
        reloj: IReloj,
    ):
        self.importaciones, self.eventos, self.uow, self.reloj = importaciones, eventos, uow, reloj

    def ejecutar(self, entrada: FallarImportacionInputDTO) -> None:
        with self.uow:
            formato = self.importaciones.fallar(entrada.importacion_id, entrada.mensaje[:1000], self.reloj.ahora())
            if formato is not None:
                self.eventos.publicar(ImportacionTerminadaEvent(entrada.importacion_id, str(formato), completada=False))
