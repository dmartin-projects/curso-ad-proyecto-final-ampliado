# asistente/application/ports/i_tipo_de_cambio.py — convertir importes entre monedas (módulo 95)
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from asistente.domain.read_models.conversion import Conversion


class ITipoDeCambio(ABC):
    @abstractmethod
    def convertir(self, importe: Decimal, de: str, a: str, fecha: date | None = None) -> Conversion:
        """Con el tipo de referencia del BCE de esa fecha (sin fecha, el último publicado).

        Lanza MonedaDesconocidaException o ServicioExternoNoDisponibleException."""
