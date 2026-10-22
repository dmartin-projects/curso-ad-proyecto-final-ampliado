# core/domain/vo/delegacion.py — una aplicación que actúa en nombre de un usuario (módulo 90)
from dataclasses import dataclass

from core.domain.enums.rol import Rol


@dataclass(frozen=True, slots=True)
class Delegacion:
    """Módulo 90: la credencial de una petición que hace una aplicación EN NOMBRE de un usuario (o en el suyo
    propio, un servicio). La construye el adapter de autenticación OAuth y viaja en `request.auth`; las views
    la usan para limitar el Actor (`Actor.limitado_a(delegacion.techo)`) y comprobar los scopes.

    `techo`: lo máximo que sus scopes permiten en un hogar (gastos:leer → LECTOR, gastos:escribir → MIEMBRO).
    Ningún scope delega el rol de administrador: gestionar el hogar no se delega a una aplicación.
    """

    cliente_id: str
    scopes: frozenset[str]
    techo: Rol | None = None

    def permite(self, scope: str) -> bool:
        return scope in self.scopes
