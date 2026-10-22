# eventos/application/ports/i_broker.py — a dónde publica el relay (Kafka) (módulos 85 y 88)
from abc import ABC, abstractmethod

from eventos.domain.bo.evento_pendiente import EventoPendiente


class IBroker(ABC):
    @abstractmethod
    def publicar(self, lote: list[EventoPendiente]) -> None:
        """Envía el lote en orden y espera la confirmación de TODO: si falta alguna, PublicacionNoConfirmadaException."""
