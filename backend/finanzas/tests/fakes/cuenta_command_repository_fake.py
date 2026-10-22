# finanzas/tests/fakes/cuenta_command_repository_fake.py — ICuentaCommandRepository en memoria (módulo 87)
from finanzas.domain.exceptions.cuenta_con_movimientos_exception import CuentaConMovimientosException
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from finanzas.tests.fakes.movimiento_command_repository_fake import MovimientoCommandRepositoryFake


class CuentaCommandRepositoryFake(ICuentaCommandRepository):
    def __init__(self, *cuentas: tuple[int, int], movimientos: MovimientoCommandRepositoryFake | None = None):
        self._cuentas = set(cuentas)  # (hogar_id, cuenta_id)
        self._movimientos = movimientos

    def existe(self, hogar_id, cuenta_id):
        return (hogar_id, cuenta_id) in self._cuentas

    # ── Ejercicio 1 ──
    def tiene_movimientos(self, cuenta_id):
        return any(m.cuenta_id == cuenta_id for m in self._movimientos.todos())

    def eliminar(self, hogar_id, cuenta_id):
        if self.tiene_movimientos(cuenta_id):
            raise CuentaConMovimientosException()  # como el RESTRICT de la base de datos
        self._cuentas.discard((hogar_id, cuenta_id))
