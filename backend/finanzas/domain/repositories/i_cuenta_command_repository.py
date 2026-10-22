# finanzas/domain/repositories/i_cuenta_command_repository.py (módulo 87)
from abc import ABC, abstractmethod


class ICuentaCommandRepository(ABC):
    @abstractmethod
    def existe(self, hogar_id: int, cuenta_id: int) -> bool: ...

    # ── Ejercicio 1: la primera regla de las cuentas ──
    @abstractmethod
    def tiene_movimientos(self, cuenta_id: int) -> bool: ...

    @abstractmethod
    def eliminar(self, hogar_id: int, cuenta_id: int) -> None:
        """Si aún tiene movimientos (otra petición los ha creado entretanto): CuentaConMovimientosException."""
