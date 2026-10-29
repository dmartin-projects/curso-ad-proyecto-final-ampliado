# finanzas/domain/repositories/i_movimiento_query_service.py — el lado de LECTURA de los movimientos (CQRS, módulo 87)
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from datetime import date

from core.domain.read_models.pagina import Pagina
from core.domain.vo.mes import Mes
from finanzas.domain.read_models.movimiento_del_mes import MovimientoDelMes
from finanzas.domain.read_models.movimiento_exportado import MovimientoExportado
from finanzas.domain.read_models.movimiento_listado import MovimientoListado
from finanzas.domain.read_models.movimiento_sin_conciliar import MovimientoSinConciliar
from finanzas.domain.read_models.totales_de_movimientos import TotalesDeMovimientos
from finanzas.domain.repositories.queries.movimientos_query import MovimientosQuery


class IMovimientoQueryService(ABC):
    """Lee sin cargar BOs: la misma frontera para la API, un comando o una tool del agente (Parte 7)."""

    @abstractmethod
    def listar(self, query: MovimientosQuery) -> Pagina[MovimientoListado]:
        """Una página de los movimientos del hogar que cumplen los filtros. Por cursor (los más recientes primero)
        o, si se pide un orden, por número de página."""

    @abstractmethod
    def detalle(self, hogar_id: int, movimiento_id: int) -> MovimientoListado | None:
        """El movimiento de ESE hogar, o None. Sin contar sus adjuntos (num_adjuntos=None): eso es del listado."""

    @abstractmethod
    def exportar(self, query: MovimientosQuery) -> Iterator[MovimientoExportado]:
        """Todos los que cumplen los filtros, en el orden pedido, sin cargarlos de golpe en memoria."""

    @abstractmethod
    def totales(self, query: MovimientosQuery) -> TotalesDeMovimientos:
        """Cuántos cumplen los filtros y cuánto suman sus gastos y sus ingresos, en una consulta (módulo 95: lo que
        necesita el agente para contestar "¿cuánto en Mercadona este año?" sin leer los movimientos uno a uno)."""

    # ── Lo que leen otras apps (módulo 88) ──
    @abstractmethod
    def del_mes(self, hogar_id: int, mes: Mes) -> list[MovimientoDelMes]:
        """Los del mes agrupables por categoría: por nombre de categoría, categoría, fecha e id (el informe)."""

    @abstractmethod
    def huellas_existentes(self, cuenta_id: int, huellas: Iterable[str]) -> set[str]:
        """Cuáles de esas filas del banco ya están en la cuenta (importadas o conciliadas)."""

    @abstractmethod
    def sin_conciliar(self, cuenta_id: int, desde: date, hasta: date) -> list[MovimientoSinConciliar]:
        """Los movimientos de la cuenta en esas fechas que aún no tienen fila del banco, en el orden de siempre."""
