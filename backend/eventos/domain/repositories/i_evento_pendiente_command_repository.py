# eventos/domain/repositories/i_evento_pendiente_command_repository.py — el lado de escritura del relay (módulos 85 y 88)
from abc import ABC, abstractmethod
from datetime import datetime

from eventos.domain.bo.evento_pendiente import EventoPendiente


class IEventoPendienteCommandRepository(ABC):
    """La bandeja de salida del relay: lo que falta por publicar y marcarlo como publicado."""

    @abstractmethod
    def pendientes(self, tamano: int) -> list[EventoPendiente]:
        """Los más antiguos sin publicar, en orden de id y BLOQUEADOS hasta el final de la transacción."""

    @abstractmethod
    def marcar_publicados(self, ids: list[int], cuando: datetime) -> None: ...
