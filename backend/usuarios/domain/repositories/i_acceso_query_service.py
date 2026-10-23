# usuarios/domain/repositories/i_acceso_query_service.py — lectura: las formas de entrar (módulo 91)
from abc import ABC, abstractmethod

from usuarios.domain.read_models.acceso import Acceso


class IAccesoQueryService(ABC):
    @abstractmethod
    def de_usuario(self, usuario_id: int) -> Acceso:
        """Las formas de entrar de una cuenta, para la pantalla «Métodos de acceso»."""
