# usuarios/tests/fakes/proveedores_fake.py — IProveedores en memoria (módulo 91)
from usuarios.application.ports.i_proveedores import IProveedores
from usuarios.domain.exceptions.proveedor_no_disponible_exception import ProveedorNoDisponibleException
from usuarios.tests.fakes.proveedor_identidad_fake import ProveedorIdentidadFake


class ProveedoresFake(IProveedores):
    def __init__(self, *proveedores: ProveedorIdentidadFake):
        self.todos = {p.proveedor: p for p in proveedores}

    def disponibles(self):
        return list(self.todos)

    def de(self, proveedor):
        if proveedor not in self.todos:
            raise ProveedorNoDisponibleException()
        return self.todos[proveedor]
