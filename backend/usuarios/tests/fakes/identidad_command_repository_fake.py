# usuarios/tests/fakes/identidad_command_repository_fake.py — IIdentidadCommandRepository en memoria (módulo 91)
from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.exceptions.identidad_de_otra_cuenta_exception import IdentidadDeOtraCuentaException
from usuarios.domain.exceptions.proveedor_ya_vinculado_exception import ProveedorYaVinculadoException
from usuarios.domain.repositories.i_identidad_command_repository import IIdentidadCommandRepository


class IdentidadCommandRepositoryFake(IIdentidadCommandRepository):
    def __init__(self):
        self.filas: dict[tuple[Proveedor, str], int] = {}  # (proveedor, sub) → usuario
        self.usos: list[tuple[Proveedor, str]] = []

    def dueno(self, proveedor, sub):
        return self.filas.get((proveedor, sub))

    def de_usuario(self, usuario_id):
        return {p: sub for (p, sub), u in self.filas.items() if u == usuario_id}

    def vincular(self, usuario_id, perfil):
        if (perfil.proveedor, perfil.sub) in self.filas:
            raise IdentidadDeOtraCuentaException(proveedor=perfil.proveedor.nombre)
        if perfil.proveedor in self.de_usuario(usuario_id):
            raise ProveedorYaVinculadoException(proveedor=perfil.proveedor.nombre)
        self.filas[(perfil.proveedor, perfil.sub)] = usuario_id

    def anotar_uso(self, proveedor, sub):
        self.usos.append((proveedor, sub))

    def desvincular(self, usuario_id, proveedor):
        self.filas = {k: u for k, u in self.filas.items() if not (u == usuario_id and k[0] == proveedor)}
