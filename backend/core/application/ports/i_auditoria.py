# core/application/ports/i_auditoria.py (módulos 17 y 87)
from abc import ABC, abstractmethod

from core.domain.bo.i_auditable import IAuditable
from core.domain.enums.accion import Accion


class IAuditoria(ABC):
    @abstractmethod
    def registrar(
        self, accion: Accion, objeto: IAuditable, usuario_id: int | None, antes: IAuditable | None = None
    ) -> None: ...

    @abstractmethod
    def registrar_varios(
        self, accion: Accion, objetos: list[IAuditable], usuario_id: int | None, antes: list[IAuditable] | None = None
    ) -> None:
        """Lo mismo para muchos a la vez (recategorizar 1.000 movimientos): `antes[i]` es el de `objetos[i]`."""
