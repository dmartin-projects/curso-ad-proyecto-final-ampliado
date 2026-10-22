# finanzas/domain/repositories/i_movimiento_query_service.py — el lado de LECTURA de los movimientos (CQRS, módulo 87)
from abc import ABC, abstractmethod
from collections.abc import Iterator

from core.domain.read_models.pagina import Pagina
from finanzas.domain.read_models.movimiento_exportado import MovimientoExportado
from finanzas.domain.read_models.movimiento_listado import MovimientoListado
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
