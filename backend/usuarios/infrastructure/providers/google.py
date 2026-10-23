# usuarios/infrastructure/providers/google.py — Sign in with Google: OpenID Connect completo (módulo 91)
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.infrastructure.providers.proveedor_oidc import ProveedorOIDC


class Google(ProveedorOIDC):
    proveedor = Proveedor.GOOGLE
    scope = "openid email profile"
    # Con varias cuentas de Google en el navegador, que la persona elija (y no entre con la del trabajo sin darse cuenta)
    parametros_extra = {"prompt": "select_account"}

    def emisores(self):
        # Google documenta los dos: "https://accounts.google.com" y "accounts.google.com" (sin esquema)
        return [self.emisor, self.emisor.removeprefix("https://")]
