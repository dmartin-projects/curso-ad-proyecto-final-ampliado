# asistente/domain/repositories/i_plan_del_hogar_repository.py — qué plan tiene cada hogar (módulo 98)
from abc import ABC, abstractmethod

from asistente.domain.enums.plan import Plan


class IPlanDelHogarRepository(ABC):
    @abstractmethod
    def plan_de(self, hogar_id: int) -> Plan:
        """El básico si nadie le ha asignado otro."""

    @abstractmethod
    def asignar(self, hogar_id: int, plan: Plan) -> None: ...
