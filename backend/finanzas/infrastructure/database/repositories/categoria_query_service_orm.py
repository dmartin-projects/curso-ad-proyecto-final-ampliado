# finanzas/infrastructure/database/repositories/categoria_query_service_orm.py — ICategoriaQueryService con el ORM
# (módulo 87)
from core.domain.repositories.queries.listado_del_hogar_query import ListadoDelHogarQuery
from finanzas.domain.read_models.categoria_listada import CategoriaListada
from finanzas.domain.repositories.i_categoria_query_service import ICategoriaQueryService
from finanzas.infrastructure.database.models.categoria_model import Categoria as CategoriaModel


def _a_read_model(c) -> CategoriaListada:
    return CategoriaListada(*c)


CAMPOS = ("pk", "nombre", "padre_id", "color", "icono", "orden", "es_ingreso")  # values_list: sin instancias


class CategoriaQueryServiceORM(ICategoriaQueryService):
    def listar(self, query: ListadoDelHogarQuery) -> list[CategoriaListada]:
        qs = CategoriaModel.objects.filter(hogar_id=query.hogar_id)  # sin orden pedido: el del modelo
        if query.orden:
            qs = qs.order_by(*query.orden)
        return [_a_read_model(c) for c in qs.values_list(*CAMPOS)]

    def detalle(self, hogar_id: int, categoria_id: int) -> CategoriaListada | None:
        fila = CategoriaModel.objects.filter(hogar_id=hogar_id, pk=categoria_id).values_list(*CAMPOS).first()
        return None if fila is None else _a_read_model(fila)
