# usuarios/application/listar_proveedores_use_case/i_listar_proveedores_use_case.py (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.listar_proveedores_use_case.dtos.proveedor_output_dto import ProveedorOutputDTO


class IListarProveedoresUseCase(ABC):
    @abstractmethod
    def ejecutar(self) -> list[ProveedorOutputDTO]: ...
