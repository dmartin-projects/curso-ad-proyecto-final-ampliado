# estadisticas/domain/repositories/i_movimiento_query_service.py — el lado de LECTURA (CQRS, módulo 89)
#
# Las agregaciones de las estadísticas. Devuelve read models del dominio (domain/read_models), no DTOs: el dominio
# no puede importar application. Cada use case de consulta los traduce a su OutputDTO.
from abc import ABC, abstractmethod
from decimal import Decimal

from estadisticas.domain.read_models.mes_de_tendencia import MesDeTendencia
from estadisticas.domain.read_models.mes_sin_revisar import MesSinRevisar
from estadisticas.domain.repositories.queries.periodo_del_hogar_query import PeriodoDelHogarQuery


class IMovimientoQueryService(ABC):
    @abstractmethod
    def tendencia(self, query: PeriodoDelHogarQuery) -> list[MesDeTendencia]:
        """Gastos, ingresos y ahorro de cada mes del periodo, también de los que no tienen movimientos."""

    @abstractmethod
    def gasto_por_dia_de_la_semana(self, query: PeriodoDelHogarQuery) -> dict[int, Decimal]:
        """{1: lo gastado en lunes, …}: solo los días con gastos."""

    @abstractmethod
    def sin_revisar(self, query: PeriodoDelHogarQuery) -> list[MesSinRevisar]:
        """Cuántos movimientos sin revisar (y cuánto gasto) hay en cada mes del periodo."""
