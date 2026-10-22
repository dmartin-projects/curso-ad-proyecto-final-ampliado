# estadisticas/application/ports/i_aparcados.py — la dead letter queue (módulos 85 y 89)
from abc import ABC, abstractmethod

from estadisticas.application.shared.dtos.mensaje_input_dto import MensajeInputDTO


class IAparcados(ABC):
    """Dónde van los mensajes que nunca se podrán aplicar (dead letter queue), con el error y su origen."""

    @abstractmethod
    def aparcar(self, mensaje: MensajeInputDTO, error: Exception) -> None: ...

    @abstractmethod
    def confirmar(self) -> None:
        """Espera a que lo aparcado esté a salvo. Si no lo está, lanza: mejor repetir el lote que perderlo."""
