# core/domain/bo/i_auditable.py — lo que la auditoría necesita de un business object (módulo 87)
from abc import ABC, abstractmethod
from typing import ClassVar


class IAuditable(ABC):
    """La implementan los BOs que se auditan (Movimiento, Categoria). El port IAuditoria solo conoce esto."""

    tipo: ClassVar[str]  # "finanzas.movimiento": app y modelo, como los ContentType
    id: int | None

    @abstractmethod
    def datos_auditables(self) -> dict:
        """Los campos que compara la auditoría, con los nombres de siempre (los de model_to_dict)."""
