# informes/domain/repositories/i_informe_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from core.domain.vo.mes import Mes
from informes.domain.read_models.informe_listado import InformeListado


class IInformeQueryService(ABC):
    @abstractmethod
    def listar(self, hogar_id: int) -> list[InformeListado]:
        """Los del hogar, del más reciente al más antiguo."""

    @abstractmethod
    def detalle(self, hogar_id: int, mes: Mes) -> InformeListado | None: ...

    @abstractmethod
    def hogares_sin_informe(self, mes: Mes) -> list[int]:
        """Los hogares con movimientos ese mes que aún no tienen su informe (la tarea de Beat del día 1)."""

    @abstractmethod
    def destinatarios(self, informe_id: int) -> list[int]:
        """Los miembros activos del hogar del informe: a quién se envía por email."""
