# notificaciones/application/ports/i_destinatarios.py (módulo 88)
from abc import ABC, abstractmethod


class IDestinatarios(ABC):
    """Quién recibe los avisos: lectura entre apps (los usuarios y sus idiomas, las membresías)."""

    @abstractmethod
    def idiomas(self, usuario_ids: list[int]) -> dict[int, str]:
        """{usuario: idioma} de los que existen."""

    @abstractmethod
    def miembros_activos(self, hogar_id: int) -> list[int]: ...

    @abstractmethod
    def hogares(self, usuario_id: int) -> list[int]:
        """Los hogares de los que es miembro (los grupos de su WebSocket)."""
