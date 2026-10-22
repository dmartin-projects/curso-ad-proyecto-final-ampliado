# finanzas/domain/repositories/i_movimiento_command_repository.py — el lado de ESCRITURA (CQRS, módulo 87)
#
# SOLO lo que necesita la escritura: cargar el BO, guardarlo, borrarlo y una operación en bloque. Los listados,
# los filtros y el CSV no están aquí: son lectura (query services). Dos implementaciones: la del ORM
# (infrastructure/database/repositories) y la de memoria (tests/fakes).
from abc import ABC, abstractmethod
from collections.abc import Iterable

from core.domain.vo.mes import Mes
from finanzas.domain.bo.movimiento import Movimiento


class IMovimientoCommandRepository(ABC):
    @abstractmethod
    def obtener(self, hogar_id: int, movimiento_id: int) -> Movimiento:
        """El movimiento de ESE hogar. Si no existe o es de otro: MovimientoNoEncontradoException."""

    @abstractmethod
    def obtener_varios(self, hogar_id: int, ids: Iterable[int]) -> list[Movimiento]:
        """Los de `ids` que sean de ESE hogar, ordenados por id. Los demás no existen para quien pregunta."""

    @abstractmethod
    def guardar(self, movimiento: Movimiento) -> None:
        """Inserta o actualiza. Si es nuevo, le pone el id."""

    @abstractmethod
    def eliminar(self, movimiento: Movimiento) -> None: ...

    @abstractmethod
    def actualizar_en_bloque(self, hogar_id: int, ids: Iterable[int], cambios: dict) -> tuple[list[int], set[Mes]]:
        """Aplica `cambios` a los movimientos de `ids` que sean del hogar, en una sola operación.
        Devuelve los ids afectados y sus meses."""
