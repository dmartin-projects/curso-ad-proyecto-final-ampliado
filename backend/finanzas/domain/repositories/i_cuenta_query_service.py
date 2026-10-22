# finanzas/domain/repositories/i_cuenta_query_service.py (módulos 87 y 88)
from abc import ABC, abstractmethod

from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from finanzas.domain.read_models.cuenta_con_saldo import CuentaConSaldo


class ICuentaQueryService(ABC):
    @abstractmethod
    def listar(self, query: ListadoDelHogarQuery) -> list[CuentaConSaldo]:
        """Las cuentas del hogar con su saldo (la suma de sus movimientos), por nombre si no se pide otro orden."""

    @abstractmethod
    def detalle(self, hogar_id: int, cuenta_id: int) -> CuentaConSaldo | None: ...

    @abstractmethod
    def existe(self, hogar_id: int, cuenta_id: int) -> bool:
        """¿Es una cuenta de ESE hogar? Sin calcular el saldo (lo preguntan los tickets y los extractos)."""
