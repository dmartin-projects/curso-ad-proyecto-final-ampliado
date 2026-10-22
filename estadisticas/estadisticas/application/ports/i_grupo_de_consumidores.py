# estadisticas/application/ports/i_grupo_de_consumidores.py — el consumer group, para reconstruir (módulo 89)
from abc import ABC, abstractmethod


class IGrupoDeConsumidores(ABC):
    @abstractmethod
    def olvidar(self) -> None:
        """Olvida hasta dónde ha leído el grupo: el próximo arranque lee los topics desde el principio.
        ConsumidorActivoException si hay alguno conectado."""
