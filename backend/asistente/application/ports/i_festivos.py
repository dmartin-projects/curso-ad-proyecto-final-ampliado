# asistente/application/ports/i_festivos.py — el calendario de festivos oficiales (módulo 95, ejercicio 1)
from abc import ABC, abstractmethod

from asistente.domain.read_models.festivo import Festivo


class IFestivos(ABC):
    @abstractmethod
    def del_anio(self, anio: int, pais: str) -> tuple[Festivo, ...]:
        """Los festivos oficiales de un año en un país (ISO 3166-1: "ES"), nacionales y autonómicos, por fecha.

        Lanza ServicioExternoNoDisponibleException."""
