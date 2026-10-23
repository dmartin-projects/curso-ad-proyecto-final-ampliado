# usuarios/domain/vo/transaccion_social.py — lo que se recuerda entre la ida al proveedor y la vuelta (módulos 91 y 92)
from dataclasses import dataclass

from usuarios.domain.enums.proposito import Proposito
from usuarios.domain.enums.proveedor import Proveedor


@dataclass(frozen=True, slots=True)
class TransaccionSocial:
    """Lo que Gastos recuerda entre la ida al proveedor y la vuelta: unos minutos y un solo uso."""

    proveedor: Proveedor
    state: str  # vuelve tal cual: la respuesta es de ESTA petición (CSRF en la vuelta)
    nonce: str  # va dentro del ID token: ese ID token es de ESTA autenticación (replay, code injection)
    code_verifier: str  # PKCE, si el proveedor lo admite: un code robado no se canjea sin él
    proposito: Proposito
    volver: str = "/"  # la ruta de la SPA tras entrar (ya comprobada con destino_seguro)
    usuario_id: int | None = None  # quién vincula (Proposito.VINCULAR) o se reautentica (REAUTENTICAR)
    sid: str | None = None  # módulo 92, ej. 3: la sesión que se reautentica
    desde: int | None = None  # ídem: cuándo empezó (unix): el proveedor tiene que autenticar DESPUÉS
