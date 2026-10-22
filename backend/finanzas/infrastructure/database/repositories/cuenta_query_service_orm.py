# finanzas/infrastructure/database/repositories/cuenta_query_service_orm.py — ICuentaQueryService con el ORM
# (módulo 87)
from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce

from finanzas.domain.read_models.cuenta_con_saldo import CuentaConSaldo
from finanzas.domain.repositories.i_cuenta_query_service import ICuentaQueryService
from finanzas.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from finanzas.infrastructure.database.models.cuenta_model import Cuenta as CuentaModel


def _a_read_model(c: CuentaModel) -> CuentaConSaldo:
    return CuentaConSaldo(id=c.pk, nombre=c.nombre, tipo=c.tipo, iban=c.iban, activa=c.activa, saldo=c.saldo)


class CuentaQueryServiceORM(ICuentaQueryService):
    @staticmethod
    def _con_saldo(hogar_id: int):
        return CuentaModel.objects.filter(hogar_id=hogar_id).annotate(
            saldo=Coalesce(Sum("movimientos__importe"), Value(0), output_field=DecimalField())
        )

    def listar(self, query: ListadoDelHogarQuery) -> list[CuentaConSaldo]:
        return [_a_read_model(c) for c in self._con_saldo(query.hogar_id).order_by(*(query.orden or ("nombre",)))]

    def detalle(self, hogar_id: int, cuenta_id: int) -> CuentaConSaldo | None:
        fila = self._con_saldo(hogar_id).filter(pk=cuenta_id).first()
        return None if fila is None else _a_read_model(fila)
