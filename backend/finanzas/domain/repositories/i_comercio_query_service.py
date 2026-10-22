# finanzas/domain/repositories/i_comercio_query_service.py (módulos 74 y 87)
from abc import ABC, abstractmethod

from core.domain.read_models.pagina import Pagina
from finanzas.domain.read_models.comercio_listado import ComercioListado
from finanzas.domain.repositories.queries.comercios_query import ComerciosQuery


class IComercioQueryService(ABC):
    @abstractmethod
    def listar(self, query: ComerciosQuery) -> Pagina[ComercioListado]:
        """Los comercios conocidos (son de todos los hogares) cuyo nombre contiene cada término, por nombre."""
