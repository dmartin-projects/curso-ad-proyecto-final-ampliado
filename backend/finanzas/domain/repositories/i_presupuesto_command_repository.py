# finanzas/domain/repositories/i_presupuesto_command_repository.py (módulos 76 y 87)
from abc import ABC, abstractmethod
from collections.abc import Iterable

from core.domain.vo.dinero import Dinero
from core.domain.vo.mes import Mes
from finanzas.domain.bo.presupuesto import Presupuesto


class IPresupuestoCommandRepository(ABC):
    @abstractmethod
    def obtener(self, hogar_id: int, presupuesto_id: int) -> Presupuesto: ...

    @abstractmethod
    def guardar(self, presupuesto: Presupuesto) -> None:
        """Inserta o actualiza. Uno por categoría y mes: PresupuestoDuplicadoException."""

    @abstractmethod
    def eliminar(self, presupuesto: Presupuesto) -> None: ...

    @abstractmethod
    def con_gastado(self, hogar_id: int, meses: Iterable[Mes]) -> list[tuple[Presupuesto, Dinero]]:
        """Los presupuestos de esos meses con lo gastado (negativo) en su categoría y subcategorías."""

    @abstractmethod
    def cambiar_alerta(self, presupuesto_id: int, *, de: bool, a: bool) -> bool:
        """Cambia alerta_enviada SOLO si sigue valiendo `de` (un UPDATE condicional). True si la ha cambiado:
        si dos procesos comprueban a la vez, solo uno gana y solo uno avisa."""
