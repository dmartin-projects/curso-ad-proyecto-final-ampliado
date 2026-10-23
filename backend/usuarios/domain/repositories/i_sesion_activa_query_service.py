# usuarios/domain/repositories/i_sesion_activa_query_service.py — lectura: la pantalla «Sesiones» (módulo 92)
from abc import ABC, abstractmethod

from usuarios.domain.read_models.sesion_activa import SesionActiva


class ISesionActivaQueryService(ABC):
    @abstractmethod
    def de_usuario(self, usuario_id: int, sid_actual: str | None) -> list[SesionActiva]:
        """Las abiertas (ni cerradas ni caducadas), la más reciente primero."""
