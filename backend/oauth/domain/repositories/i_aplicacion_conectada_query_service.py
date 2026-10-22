# oauth/domain/repositories/i_aplicacion_conectada_query_service.py — lectura (ejercicio 1 del módulo 90)
from abc import ABC, abstractmethod

from oauth.domain.read_models.aplicacion_conectada import AplicacionConectada


class IAplicacionConectadaQueryService(ABC):
    @abstractmethod
    def listar(self, usuario_id: int) -> list[AplicacionConectada]:
        """Las aplicaciones con acceso a la cuenta de este usuario, la de uso más reciente primero."""
