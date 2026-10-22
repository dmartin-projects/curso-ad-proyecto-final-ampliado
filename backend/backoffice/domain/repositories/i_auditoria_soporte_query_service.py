# backoffice/domain/repositories/i_auditoria_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.registro_auditoria_soporte import RegistroAuditoriaSoporte
from backoffice.domain.repositories.queries.listado_soporte_query import ListadoSoporteQuery
from core.domain.read_models.pagina import Pagina


class IAuditoriaSoporteQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoSoporteQuery, *, modelo: str | None = None) -> Pagina[RegistroAuditoriaSoporte]:
        """`modelo`: app.modelo (finanzas.movimiento)."""

    @abstractmethod
    def detalle(self, registro_id: int) -> RegistroAuditoriaSoporte | None: ...
