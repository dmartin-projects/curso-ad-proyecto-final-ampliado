# usuarios/infrastructure/providers/microsoft.py — Microsoft Entra ID como cuarto proveedor (módulo 91, ejercicio 1)
#
# OpenID Connect, como Google, con dos diferencias que obligan a pensar:
# - Con el endpoint `common` (cuentas personales y de cualquier empresa) el emisor no es fijo: el discovery dice
#   "https://login.microsoftonline.com/{tenantid}/v2.0" y cada ID token trae el suyo, con el `tid` de su tenant. Se
#   comprueba que `iss` es la plantilla con SU `tid`: ni otro emisor, ni un `tid` que no cuadra con el `iss`.
# - El claim `email` no está verificado: en un tenant, su administrador puede poner el email que quiera a un usuario
#   (el ataque "nOAuth"). Solo cuenta como verificado con el claim opcional `xms_edov` (email domain owner verified:
#   el tenant es dueño del dominio del email), que hay que pedir en el registro de la aplicación. Sin él, con
#   Microsoft no se crea ninguna cuenta: se vincula desde dentro (decidir_vinculo no mira el email).
import re
from dataclasses import replace

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.vo.perfil_externo import PerfilExterno
from usuarios.infrastructure.providers.proveedor_oidc import ProveedorOIDC, es_cierto

GUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")  # el formato de un tenant id


class Microsoft(ProveedorOIDC):
    proveedor = Proveedor.MICROSOFT
    scope = "openid email profile"
    parametros_extra = {"prompt": "select_account"}

    def issuer_del_discovery(self) -> str:
        return self.emisor.replace("/common/", "/{tenantid}/")  # …/common/v2.0 → …/{tenantid}/v2.0

    def iss_valido(self, iss: str, claims: dict) -> bool:
        tid = claims.get("tid")
        return isinstance(tid, str) and bool(tid) and iss == self.issuer_del_discovery().replace("{tenantid}", tid)

    def iss_de_respuesta_valido(self, iss: str) -> bool:
        """La vuelta trae el `iss` de SU tenant, que aún no se conoce (va en el ID token): aquí, que sea la plantilla
        con un tenant cualquiera; tras el canje, completar() exige que sea el mismo `iss` que el del ID token."""
        prefijo, _, sufijo = self.issuer_del_discovery().partition("{tenantid}")
        tid = iss.removeprefix(prefijo).removesuffix(sufijo) if iss.startswith(prefijo) and iss.endswith(sufijo) else ""
        return GUID.fullmatch(tid) is not None

    def _perfil(self, claims: dict, parametros: dict[str, str]) -> PerfilExterno:
        perfil = super()._perfil(claims, parametros)
        return replace(perfil, email_verificado=es_cierto(claims.get("xms_edov")))
