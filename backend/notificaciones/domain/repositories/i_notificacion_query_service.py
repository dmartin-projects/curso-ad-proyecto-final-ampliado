# notificaciones/domain/repositories/i_notificacion_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from core.domain.read_models.pagina import Pagina
from notificaciones.domain.read_models.notificacion_listada import NotificacionListada
from notificaciones.domain.repositories.queries.notificaciones_query import NotificacionesQuery


class INotificacionQueryService(ABC):
    @abstractmethod
    def listar(self, query: NotificacionesQuery) -> Pagina[NotificacionListada]:
        """Las de esa persona (de todos sus hogares), las más recientes primero."""

    @abstractmethod
    def detalle(self, usuario_id: int, notificacion_id: int) -> NotificacionListada | None:
        """None si no existe o no es suya."""

    @abstractmethod
    def contar_no_leidas(self, usuario_id: int) -> int: ...
