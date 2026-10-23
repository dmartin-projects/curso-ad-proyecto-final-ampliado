# usuarios/domain/repositories/i_identidad_command_repository.py — las identidades externas de cada cuenta (módulo 91)
from abc import ABC, abstractmethod

from usuarios.domain.enums.proveedor import Proveedor
from usuarios.domain.vo.perfil_externo import PerfilExterno


class IIdentidadCommandRepository(ABC):
    """Las identidades externas vinculadas a cada cuenta: (proveedor, sub) → usuario."""

    @abstractmethod
    def dueno(self, proveedor: Proveedor, sub: str) -> int | None: ...

    @abstractmethod
    def de_usuario(self, usuario_id: int) -> dict[Proveedor, str]:
        """Proveedor → sub, de las vinculadas a esa cuenta."""

    @abstractmethod
    def vincular(self, usuario_id: int, perfil: PerfilExterno) -> None:
        """Dos a la vez: IdentidadDeOtraCuentaException (ese sub ya es de otro) o ProveedorYaVinculadoException (ya
        tiene uno)."""

    @abstractmethod
    def anotar_uso(self, proveedor: Proveedor, sub: str) -> None: ...

    @abstractmethod
    def desvincular(self, usuario_id: int, proveedor: Proveedor) -> None: ...
