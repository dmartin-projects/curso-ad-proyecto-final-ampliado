# finanzas/tests/fakes/cuenta_command_repository_fake.py — ICuentaCommandRepository en memoria (módulo 87)
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository


class CuentaCommandRepositoryFake(ICuentaCommandRepository):
    def __init__(self, *cuentas: tuple[int, int]):
        self._cuentas = set(cuentas)  # (hogar_id, cuenta_id)

    def existe(self, hogar_id, cuenta_id):
        return (hogar_id, cuenta_id) in self._cuentas
