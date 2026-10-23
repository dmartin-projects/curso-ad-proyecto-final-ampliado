# usuarios/domain/vo/metodos_de_acceso.py — que nadie se quede sin forma de entrar (módulos 91 y 92)
from dataclasses import dataclass, replace

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.identidad_no_vinculada_exception import IdentidadNoVinculadaException
from usuarios.domain.exceptions.ultimo_metodo_de_acceso_exception import UltimoMetodoDeAccesoException


@dataclass(frozen=True, slots=True)
class MetodosDeAcceso:
    """Las formas de entrar de una cuenta: su contraseña (si tiene), sus identidades externas y (módulo 92) sus
    passkeys, que también abren la sesión por sí solas."""

    contrasena: bool
    proveedores: frozenset[Proveedor]
    passkeys: int = 0

    def sin(self, proveedor: Proveedor) -> "MetodosDeAcceso":
        if proveedor not in self.proveedores:
            raise IdentidadNoVinculadaException()
        return replace(self, proveedores=self.proveedores - {proveedor})._quedan_formas_de_entrar()

    def sin_una_passkey(self) -> "MetodosDeAcceso":
        return replace(self, passkeys=self.passkeys - 1)._quedan_formas_de_entrar()

    def _quedan_formas_de_entrar(self) -> "MetodosDeAcceso":
        if not self.contrasena and not self.proveedores and self.passkeys <= 0:
            raise UltimoMetodoDeAccesoException()
        return self
