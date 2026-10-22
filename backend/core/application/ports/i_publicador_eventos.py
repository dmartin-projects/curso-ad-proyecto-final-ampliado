# core/application/ports/i_publicador_eventos.py (módulo 87)
from abc import ABC, abstractmethod


class IPublicadorEventos(ABC):
    @abstractmethod
    def publicar(self, *eventos: object) -> None:
        """Publica los eventos de dominio DENTRO de la transacción del use case (outbox, módulo 85)."""
