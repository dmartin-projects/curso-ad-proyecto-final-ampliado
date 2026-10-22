# importaciones/application/ports/i_movimientos.py — lo que las importaciones necesitan de finanzas (módulo 88)
from abc import ABC, abstractmethod
from datetime import date

from core.domain.vo.actor import Actor
from importaciones.domain.bo.fila import Fila
from importaciones.domain.vo.candidato import Candidato


class IMovimientos(ABC):
    """Lo que las importaciones necesitan de finanzas, en SUS palabras: leer lo que ya hay y pedirle los cambios. El
    adapter (infrastructure/finanzas/) lo traduce a los query services y los use cases de finanzas."""

    @abstractmethod
    def cuenta_del_hogar(self, hogar_id: int, cuenta_id: int) -> bool: ...

    @abstractmethod
    def huellas_existentes(self, cuenta_id: int, huellas: list[str]) -> set[str]: ...

    @abstractmethod
    def candidatos(self, cuenta_id: int, desde: date, hasta: date) -> list[Candidato]:
        """Los gastos de la cuenta en esas fechas que aún no tienen fila del banco."""

    @abstractmethod
    def apuntar(self, *, hogar_id: int, actor: Actor, cuenta_id: int, filas: list[Fila]) -> list[int]:
        """Un movimiento por fila (con su huella), en el orden de las filas. Devuelve sus ids."""

    @abstractmethod
    def conciliar(self, *, hogar_id: int, actor: Actor, huellas: dict[int, str]) -> set[int]:
        """Vincula gastos con filas del banco. Devuelve los conciliados (no los que ya tenían otra fila)."""

    @abstractmethod
    def eliminar(self, *, hogar_id: int, actor: Actor, ids: list[int]) -> None: ...

    @abstractmethod
    def desconciliar(self, *, hogar_id: int, actor: Actor, ids: list[int]) -> None: ...
