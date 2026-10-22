# notificaciones/domain/repositories/i_notificacion_command_repository.py (módulo 88)
from abc import ABC, abstractmethod

from notificaciones.domain.bo.notificacion import Notificacion


class INotificacionCommandRepository(ABC):
    @abstractmethod
    def crear_varias(self, notificaciones: list[Notificacion]) -> None:
        """Todas de una vez; les pone el id."""
