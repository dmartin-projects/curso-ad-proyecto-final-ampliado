# oauth/domain/services/scopes.py — qué scopes pide cada clase de cliente, y qué significan en un hogar (módulos 90 y 104)
from collections.abc import Iterable

from core.domain.enums.rol import Rol
from oauth.domain.enums.scope import Scope

IDENTIDAD = frozenset({Scope.OPENID, Scope.PROFILE, Scope.EMAIL})
DE_LA_API = frozenset({Scope.GASTOS_LEER, Scope.GASTOS_ESCRIBIR})
DEL_USUARIO = IDENTIDAD | DE_LA_API
DE_SERVICIO = frozenset({Scope.OPERACIONES_LEER})

# Lo máximo que cada scope permite en un hogar. Ninguno llega a ADMIN: invitar, expulsar, cambiar roles o borrar el
# hogar no se delega a una aplicación, por muchos scopes que pida.
TECHO = {Scope.GASTOS_LEER: Rol.LECTOR, Scope.GASTOS_ESCRIBIR: Rol.MIEMBRO}


def techo(scopes: Iterable[str]) -> Rol | None:
    """El rol más alto que permiten estos scopes en un hogar; None si ninguno da acceso a los hogares."""
    roles = [TECHO[Scope(s)] for s in scopes if s in TECHO]
    return max(roles, key=lambda r: r.nivel, default=None)


def con_implicados(scopes: Iterable[str]) -> frozenset[str]:
    """Módulo 104: los scopes y los que van incluidos en ellos (MCP: «servers MUST account for scope hierarchies»).
    Un scope de los hogares incluye los de techo menor o igual: quien puede escribir (MIEMBRO) puede leer (LECTOR)."""
    scopes = frozenset(scopes)
    nivel = techo(scopes)
    if nivel is None:
        return scopes
    return scopes | {str(s) for s, rol in TECHO.items() if rol.nivel <= nivel.nivel}
