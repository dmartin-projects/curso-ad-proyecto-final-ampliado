# asistente/domain/repositories/i_conversacion_query_service.py — leer conversaciones y carpetas (módulo 97)
from abc import ABC, abstractmethod

from asistente.domain.read_models.carpeta_listada import CarpetaListada
from asistente.domain.read_models.conversacion_detalle import ConversacionDetalle
from asistente.domain.read_models.conversacion_listada import ConversacionListada


class IConversacionQueryService(ABC):
    @abstractmethod
    def listar(
        self,
        usuario_id: int,
        hogar_id: int,
        carpeta_id: int | None = None,
        limite: int = 50,
        busqueda: str | None = None,
    ) -> tuple[ConversacionListada, ...]:
        """Las más recientes primero; con `carpeta_id`, solo las de esa carpeta; con `busqueda` (ejercicio 2), las que
        la tienen en el título o en algún mensaje visible, sin mirar tildes ni mayúsculas."""

    @abstractmethod
    def detalle(self, usuario_id: int, hogar_id: int, conversacion_id: int) -> ConversacionDetalle | None: ...

    @abstractmethod
    def carpetas(self, usuario_id: int, hogar_id: int) -> tuple[CarpetaListada, ...]:
        """Por nombre, con cuántas conversaciones tiene cada una."""
