# finanzas/infrastructure/cache/dashboard_cache.py — la caché del dashboard, versionada por hogar (módulos 77 y 87)
#
# Un adapter que envuelve a otro (patrón decorator): DashboardQueryServiceCache cumple la misma interfaz que
# DashboardQueryServiceORM y solo calcula si en Redis no está la versión actual. El use case no sabe que hay caché;
# lo decide container.py al montarlo.
import time

from django.core.cache import cache

from finanzas.domain.read_models.dashboard import Dashboard
from finanzas.domain.repositories.i_dashboard_query_service import IDashboardQueryService
from finanzas.domain.repositories.queries.dashboard_query import DashboardQuery

DURACION = 60 * 60  # 1 h: de todos modos se invalida en cuanto cambia algo
FORMATO = 2  # sube si cambia la FORMA del read model: lo que haya en la caché con la forma vieja deja de leerse


def _clave_version(hogar_id: int) -> str:
    return f"dashboard:version:{hogar_id}"


def _inicial() -> int:
    # Empieza en "ahora" (ms), no en 1: si Redis expulsa la clave por falta de memoria, la versión nueva
    # nunca coincide con una antigua cuyos datos sigan en la caché.
    return time.time_ns() // 1_000_000


def version(hogar_id: int) -> int:
    clave = _clave_version(hogar_id)
    cache.add(clave, _inicial(), timeout=None)  # no caduca: es solo un contador
    return cache.get(clave) or _inicial()


def invalidar(hogar_id: int) -> None:
    """O(1): no hay que buscar ni borrar claves; las de versiones anteriores caducan solas."""
    clave = _clave_version(hogar_id)
    cache.add(clave, _inicial(), timeout=None)
    cache.incr(clave)  # atómico en Redis


class DashboardQueryServiceCache(IDashboardQueryService):
    def __init__(self, calculo: IDashboardQueryService):
        self.calculo = calculo

    def resumen(self, query: DashboardQuery) -> Dashboard:
        clave = f"dashboard:{query.hogar_id}:v{version(query.hogar_id)}:{query.mes}:f{FORMATO}"
        return cache.get_or_set(clave, lambda: self.calculo.resumen(query), DURACION)
