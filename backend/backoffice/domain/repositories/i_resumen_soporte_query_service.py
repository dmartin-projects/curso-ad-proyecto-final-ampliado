# backoffice/domain/repositories/i_resumen_soporte_query_service.py (módulo 88)
from abc import ABC, abstractmethod

from backoffice.domain.read_models.resumen_soporte import ResumenSoporte


class IResumenSoporteQueryService(ABC):
    @abstractmethod
    def resumen(self) -> ResumenSoporte:
        """La primera pantalla de soporte: ¿va todo bien?"""
