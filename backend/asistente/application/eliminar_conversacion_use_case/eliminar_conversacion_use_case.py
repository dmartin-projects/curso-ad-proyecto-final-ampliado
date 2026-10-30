# asistente/application/eliminar_conversacion_use_case/eliminar_conversacion_use_case.py (módulo 97)
import logging

from asistente.application.eliminar_conversacion_use_case.dtos.eliminar_conversacion_input_dto import (
    EliminarConversacionInputDTO,
)
from asistente.application.eliminar_conversacion_use_case.i_eliminar_conversacion_use_case import (
    IEliminarConversacionUseCase,
)
from asistente.application.ports.i_almacen_de_archivos import IAlmacenDeArchivos
from asistente.domain.repositories.i_conversacion_command_repository import IConversacionCommandRepository
from core.application.ports.i_unidad_de_trabajo import IUnidadDeTrabajo
from core.domain.enums.rol import Rol

logger = logging.getLogger(__name__)


class EliminarConversacionUseCase(IEliminarConversacionUseCase):
    """Borrar una conversación es borrar también lo que guardó en el almacenamiento (las fotos y los PDF adjuntos, los
    CSV exportados): si no, quedarían datos del hogar sin nada que los enseñe ni los borre. Los archivos, después del
    commit: si la base de datos falla, la conversación sigue entera; si falla el almacenamiento, queda en el log."""

    rol_minimo = Rol.LECTOR

    def __init__(
        self, *, conversaciones: IConversacionCommandRepository, almacen: IAlmacenDeArchivos, uow: IUnidadDeTrabajo
    ):
        self.conversaciones, self.almacen, self.uow = conversaciones, almacen, uow

    def ejecutar(self, entrada: EliminarConversacionInputDTO) -> None:
        entrada.actor.exigir(self.rol_minimo)
        with self.uow:
            conversacion = self.conversaciones.obtener(
                entrada.actor.usuario_id, entrada.hogar_id, entrada.conversacion_id
            )
            rutas = self.conversaciones.archivos(conversacion.id)
            self.conversaciones.eliminar(conversacion)
        for ruta in rutas:
            try:
                self.almacen.borrar(ruta)
            except Exception:
                logger.exception("No se pudo borrar %s de la conversación %s", ruta, conversacion.id)
