# finanzas/infrastructure/database/repositories/comercio_query_service_orm.py — IComercioQueryService con el ORM
# (módulos 74 y 87)
from functools import reduce
from operator import and_

from django.db.models import Q

from core.domain.read_models.pagina import Pagina
from core.infrastructure.database import paginacion
from finanzas.domain.read_models.comercio_listado import ComercioListado
from finanzas.domain.repositories.i_comercio_query_service import IComercioQueryService
from finanzas.domain.repositories.queries.comercios_query import ComerciosQuery
from finanzas.infrastructure.database.models.comercio_model import Comercio as ComercioModel


class ComercioQueryServiceORM(IComercioQueryService):
    def listar(self, query: ComerciosQuery) -> Pagina[ComercioListado]:
        qs = ComercioModel.objects.order_by("nombre")
        if query.busqueda:
            qs = qs.filter(reduce(and_, (Q(nombre__icontains=t) for t in query.busqueda)))
        return paginacion.por_numero(qs.values_list("pk", "nombre"), query.paginacion, lambda c: ComercioListado(*c))
