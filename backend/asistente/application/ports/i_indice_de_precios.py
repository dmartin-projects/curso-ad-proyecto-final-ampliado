# asistente/application/ports/i_indice_de_precios.py — la inflación oficial por grupos de gasto (módulo 95)
from abc import ABC, abstractmethod

from asistente.domain.read_models.serie_de_precios import SerieDePrecios


class IIndiceDePrecios(ABC):
    @abstractmethod
    def serie(self, grupo: str) -> SerieDePrecios:
        """Las tasas de variación anual de los últimos meses PUBLICADOS de un grupo COICOP en España. Un mes que
        todavía no se ha publicado no está en la serie (no es un cero).

        Lanza ServicioExternoNoDisponibleException."""
