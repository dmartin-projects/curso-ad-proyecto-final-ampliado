# tickets/application/ports/i_gastos.py — lo que los tickets necesitan de finanzas (módulo 88)
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal

from core.domain.vo.actor import Actor


class IGastos(ABC):
    """Lo que los tickets necesitan de finanzas, en SUS palabras. Un ticket es un GASTO: aquí se habla de su total
    (positivo); el adapter (infrastructure/finanzas/) lo convierte en el importe negativo de un movimiento."""

    @abstractmethod
    def nombres_de_categorias(self, hogar_id: int) -> list[str]: ...

    @abstractmethod
    def existe_cuenta(self, hogar_id: int, cuenta_id: int) -> bool: ...

    @abstractmethod
    def apuntar(
        self,
        *,
        hogar_id: int,
        actor: Actor,
        cuenta_id: int,
        fecha: date,
        total: Decimal,
        concepto: str,
        comercio: str,
        nif: str,
        categoria_sugerida: str,
        revisado: bool,
    ) -> int:
        """El gasto que propone el ticket (lo crea un proceso). Devuelve su id."""

    @abstractmethod
    def registrar(
        self,
        *,
        hogar_id: int,
        actor: Actor,
        cuenta_id: int,
        fecha: date,
        total: Decimal,
        concepto: str,
        categoria_id: int | None,
    ) -> int:
        """El gasto que una persona confirma a mano (el ticket no tenía total). Devuelve su id."""

    @abstractmethod
    def corregir(
        self,
        *,
        hogar_id: int,
        actor: Actor,
        movimiento_id: int,
        fecha: date,
        total: Decimal,
        concepto: str,
        categoria_id: int | None,
    ) -> None:
        """La persona revisa el gasto propuesto: queda corregido y revisado."""

    @abstractmethod
    def descartar(self, *, hogar_id: int, actor: Actor, movimiento_id: int) -> bool:
        """Borra el gasto propuesto si nadie lo ha revisado. True si lo ha borrado."""
        ...
