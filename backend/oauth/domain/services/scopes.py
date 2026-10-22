# oauth/domain/services/scopes.py — qué scopes pide cada clase de cliente, y qué significan en un hogar (módulo 90)
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
