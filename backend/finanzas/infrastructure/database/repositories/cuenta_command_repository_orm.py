# finanzas/infrastructure/database/repositories/cuenta_command_repository_orm.py (módulo 87)
from django.db import transaction
from django.db.models import RestrictedError

from finanzas.domain.exceptions.cuenta_con_movimientos_exception import CuentaConMovimientosException
from finanzas.domain.repositories.i_cuenta_command_repository import ICuentaCommandRepository
from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel
from finanzas.infrastructure.database.models.movimiento_model import Movimiento as MovimientoModel


class CuentaCommandRepositoryORM(ICuentaCommandRepository):
    def existe(self, hogar_id: int, cuenta_id: int) -> bool:
        return CuentaModel.objects.filter(hogar_id=hogar_id, pk=cuenta_id).exists()

    # ── Ejercicio 1 ──
    def tiene_movimientos(self, cuenta_id: int) -> bool:
        return MovimientoModel.objects.filter(cuenta_id=cuenta_id).exists()

    def eliminar(self, hogar_id: int, cuenta_id: int) -> None:
        try:
            with transaction.atomic():
                CuentaModel.objects.filter(hogar_id=hogar_id, pk=cuenta_id).delete()
        except RestrictedError as e:  # on_delete=RESTRICT: un movimiento creado entre la comprobación y el DELETE
            raise CuentaConMovimientosException() from e
