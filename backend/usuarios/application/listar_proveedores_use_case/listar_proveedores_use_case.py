# usuarios/application/listar_proveedores_use_case/listar_proveedores_use_case.py — con qué se puede entrar (módulo 91)
from usuarios.application.listar_proveedores_use_case.dtos.proveedor_output_dto import ProveedorOutputDTO
from usuarios.application.listar_proveedores_use_case.i_listar_proveedores_use_case import IListarProveedoresUseCase
from usuarios.application.ports.i_proveedores import IProveedores


class ListarProveedoresUseCase(IListarProveedoresUseCase):
    """Los proveedores configurados en este entorno, en el orden en que se ofrecen."""

    def __init__(self, *, proveedores: IProveedores):
        self.proveedores = proveedores

    def ejecutar(self) -> list[ProveedorOutputDTO]:
        return [ProveedorOutputDTO(p.value, p.nombre) for p in self.proveedores.disponibles()]
