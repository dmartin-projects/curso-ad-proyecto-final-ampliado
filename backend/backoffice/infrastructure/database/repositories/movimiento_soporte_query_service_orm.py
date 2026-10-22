# backoffice/infrastructure/database/repositories/movimiento_soporte_query_service_orm.py — IMovimientoSoporteQueryService con el ORM (módulo 88)
from backoffice.domain.read_models.movimiento_soporte import MovimientoSoporte
from backoffice.domain.repositories.i_movimiento_soporte_query_service import IMovimientoSoporteQueryService
from backoffice.infrastructure.database.repositories.listados import listar
from finanzas.models import Categoria as CategoriaModel
from finanzas.models import Movimiento as MovimientoModel

BUSQUEDA = ("concepto", "comercio__nombre")


def _a_read_model(m: MovimientoModel) -> MovimientoSoporte:
    return MovimientoSoporte(
        id=m.pk,
        hogar_id=m.hogar_id,
        fecha=m.fecha,
        importe=m.importe,
        concepto=m.concepto,
        categoria_id=m.categoria_id,
        categoria_nombre=None if m.categoria is None else m.categoria.nombre,
        origen=m.origen,
        revisado=m.revisado,
    )


class MovimientoSoporteQueryServiceORM(IMovimientoSoporteQueryService):
    @staticmethod
    def _todos():
        return MovimientoModel.objects.select_related("categoria")

    def listar(self, query):
        return listar(self._todos(), query, BUSQUEDA, _a_read_model)

    def detalle(self, movimiento_id):
        fila = self._todos().filter(pk=movimiento_id).first()
        return None if fila is None else _a_read_model(fila)

    def hogar_de_categoria(self, categoria_id):
        return CategoriaModel.objects.filter(pk=categoria_id).values_list("hogar_id", flat=True).first()
