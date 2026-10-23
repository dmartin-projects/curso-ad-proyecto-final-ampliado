# usuarios/domain/repositories/i_seguridad_query_service.py — lectura: la pantalla «Seguridad» (módulo 92)
from abc import ABC, abstractmethod

from usuarios.domain.read_models.seguridad import Seguridad


class ISeguridadQueryService(ABC):
    @abstractmethod
    def de_usuario(self, usuario_id: int) -> Seguridad:
        """La verificación en dos pasos y las passkeys de una cuenta, para la pantalla «Seguridad»."""
