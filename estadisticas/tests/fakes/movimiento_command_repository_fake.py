"""IMovimientoCommandRepository en memoria (módulo 89): solo gana una versión más nueva, y lo que no cabría en
PostgreSQL es un EventoInvalidoException. Que se porta igual que el de SQLAlchemy lo comprueban los contract tests
(tests/infrastructure/database/repositories/test_command_repositories.py)."""

from decimal import Decimal

from estadisticas.domain.bo.movimiento import Movimiento
from estadisticas.domain.exceptions.evento_invalido_exception import EventoInvalidoException
from estadisticas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository
from tests.fakes.memoria import Memoria

CABE = Decimal("1e10")  # Numeric(12, 2): diez dígitos enteros


class MovimientoCommandRepositoryFake(IMovimientoCommandRepository):
    def __init__(self, memoria: Memoria):
        self.memoria = memoria

    def guardar(self, movimiento: Movimiento) -> bool:
        if abs(movimiento.importe) >= CABE:
            raise EventoInvalidoException(ValueError("numeric field overflow"))
        actual = self.memoria.movimientos.get(movimiento.id)
        if actual is not None and actual.version >= movimiento.version:
            return False
        self.memoria.movimientos[movimiento.id] = movimiento
        return True

    def eliminar(self, movimiento_id: int, version: int) -> bool:
        actual = self.memoria.movimientos.get(movimiento_id)
        if actual is None or actual.version >= version:
            return False
        del self.memoria.movimientos[movimiento_id]
        return True

    def vaciar(self) -> None:
        self.memoria.movimientos.clear()
