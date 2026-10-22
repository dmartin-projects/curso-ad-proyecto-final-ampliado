# finanzas/domain/repositories/i_cuenta_query_service.py (módulo 87)
from abc import ABC, abstractmethod

from finanzas.domain.read_models.cuenta_con_saldo import CuentaConSaldo
from finanzas.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery


class ICuentaQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoDelHogarQuery) -> list[CuentaConSaldo]:
        """Las cuentas del hogar con su saldo (la suma de sus movimientos), por nombre si no se pide otro orden."""

    @abstractmethod
    def detalle(self, hogar_id: int, cuenta_id: int) -> CuentaConSaldo | None: ...
