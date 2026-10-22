# oauth/domain/repositories/i_cliente_command_repository.py — las aplicaciones registradas (módulo 90)
from abc import ABC, abstractmethod

from oauth.domain.bo.cliente_nuevo import ClienteNuevo
from oauth.domain.vo.credenciales import Credenciales


class IClienteCommandRepository(ABC):
    """Las aplicaciones registradas en el authorization server (en Django: las Application de django-oauth-toolkit)."""

    @abstractmethod
    def existe(self, client_id: str) -> bool: ...

    @abstractmethod
    def crear(self, cliente: ClienteNuevo) -> Credenciales:
        """El client_id (el pedido o uno aleatorio) y, si es confidencial, un secreto nuevo que no se vuelve a ver."""
