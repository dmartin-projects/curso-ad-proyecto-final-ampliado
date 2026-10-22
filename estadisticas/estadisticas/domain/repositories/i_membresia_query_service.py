# estadisticas/domain/repositories/i_membresia_query_service.py — el lado de LECTURA (CQRS, módulo 89)
from abc import ABC, abstractmethod


class IMembresiaQueryService(ABC):
    @abstractmethod
    def es_miembro(self, hogar_id: int, usuario_id: int) -> bool: ...
