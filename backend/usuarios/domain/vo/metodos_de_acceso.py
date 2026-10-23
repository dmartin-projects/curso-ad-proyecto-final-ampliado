# usuarios/domain/vo/metodos_de_acceso.py — que nadie se quede sin forma de entrar (módulo 91)
from dataclasses import dataclass, replace

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.identidad_no_vinculada_exception import IdentidadNoVinculadaException
from usuarios.domain.exceptions.ultimo_metodo_de_acceso_exception import UltimoMetodoDeAccesoException


@dataclass(frozen=True, slots=True)
class MetodosDeAcceso:
    """Las formas de entrar de una cuenta: su contraseña (si tiene) y sus identidades externas."""

    contrasena: bool
    proveedores: frozenset[Proveedor]

    def sin(self, proveedor: Proveedor) -> "MetodosDeAcceso":
        if proveedor not in self.proveedores:
            raise IdentidadNoVinculadaException()
        quedan = replace(self, proveedores=self.proveedores - {proveedor})
        if not quedan.contrasena and not quedan.proveedores:
            raise UltimoMetodoDeAccesoException()
        return quedan
