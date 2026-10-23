# usuarios/application/ports/i_proveedores.py — los proveedores configurados (módulo 91)
from abc import ABC, abstractmethod

from usuarios.application.ports.i_proveedor_identidad import IProveedorIdentidad
from usuarios.domain.enums.proveedor import Proveedor


class IProveedores(ABC):
    @abstractmethod
    def disponibles(self) -> list[Proveedor]:
        """Los configurados (con client_id), en el orden en que se ofrecen."""

    @abstractmethod
    def de(self, proveedor: Proveedor) -> IProveedorIdentidad:
        """ProveedorNoDisponibleException si no está configurado."""
