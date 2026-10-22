# estadisticas/application/ports/i_traza.py — lo que se anota de un mensaje mientras se procesa (módulo 89)
from abc import ABC, abstractmethod

from estadisticas.domain.enums.resultado import Resultado


class ITraza(ABC):
    @abstractmethod
    def resultado(self, resultado: Resultado) -> None: ...
