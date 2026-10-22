# hogares/domain/repositories/i_invitacion_command_repository.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.domain.bo.invitacion import Invitacion


class IInvitacionCommandRepository(ABC):
    @abstractmethod
    def pendiente(self, hogar_id: int, email: str) -> Invitacion | None: ...

    @abstractmethod
    def por_token(self, token: str) -> Invitacion | None:
        """Bloqueada hasta el final de la transacción: dos clics en el enlace no aceptan dos veces."""

    @abstractmethod
    def guardar(self, invitacion: Invitacion) -> None: ...
