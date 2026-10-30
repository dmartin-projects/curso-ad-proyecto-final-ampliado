# asistente/domain/repositories/i_consumo_query_service.py — sumas del libro de cuentas (módulo 98)
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal

from asistente.domain.read_models.coste_por_hogar import CostePorHogar


class IConsumoQueryService(ABC):
    @abstractmethod
    def tokens(self, usuario_id: int, hogar_id: int, desde: datetime) -> int:
        """Entrada + salida de esa persona en ese hogar, desde ese momento (la caché cuenta: el proveedor la cuenta)."""

    @abstractmethod
    def coste(self, hogar_id: int, desde: datetime) -> Decimal:
        """El coste conocido del hogar desde ese momento."""

    @abstractmethod
    def por_hogar(self, desde: datetime, hasta: datetime) -> tuple[CostePorHogar, ...]:
        """Por hogar y modelo, los que más cuestan primero."""
