# oauth/domain/bo/cliente_nuevo.py — una aplicación cliente que se registra en el authorization server (módulo 90)
import re
from dataclasses import dataclass

from oauth.domain.enums.tipo_cliente import TipoCliente
from oauth.domain.exceptions.client_id_no_valido_exception import ClientIdNoValidoException
from oauth.domain.exceptions.nombre_obligatorio_exception import NombreObligatorioException
from oauth.domain.exceptions.redirect_uri_no_valida_exception import RedirectUriNoValidaException
from oauth.domain.exceptions.scopes_no_validos_exception import ScopesNoValidosException
from oauth.domain.services.redirect_uris import validar_redirect_uri

CLIENT_ID = re.compile(r"[A-Za-z0-9._-]{3,100}")


@dataclass(frozen=True)
class ClienteNuevo:
    """Lo que se registra de un cliente. Se valida al construirse: no existe un cliente nuevo inválido."""

    nombre: str
    tipo: TipoCliente
    scopes: frozenset[str]  # los de Scope (un StrEnum: "gastos:leer" == Scope.GASTOS_LEER)
    redirect_uris: tuple[str, ...] = ()
    client_id: str | None = None  # None: lo genera el servidor (uno aleatorio)

    def __post_init__(self):
        if not self.nombre.strip():
            raise NombreObligatorioException()
        if self.client_id is not None and not CLIENT_ID.fullmatch(self.client_id):
            raise ClientIdNoValidoException()
        permitidos = self.tipo.scopes_permitidos
        if not self.scopes or not self.scopes <= permitidos:
            raise ScopesNoValidosException(f"Un cliente {self.tipo} puede pedir: {', '.join(sorted(permitidos))}.")
        if not self.tipo.con_redirect and self.redirect_uris:
            raise RedirectUriNoValidaException(
                f"Un cliente {self.tipo} no tiene redirect URIs: no vuelve por el navegador."
            )
        if self.tipo.con_redirect and not self.redirect_uris:
            raise RedirectUriNoValidaException("Hace falta al menos una redirect URI.")
        for uri in self.redirect_uris:
            validar_redirect_uri(uri)
