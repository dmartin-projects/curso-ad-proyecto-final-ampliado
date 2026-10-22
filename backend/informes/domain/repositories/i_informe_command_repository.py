# informes/domain/repositories/i_informe_command_repository.py — el lado de escritura de los informes (módulo 88)
from abc import ABC, abstractmethod

from core.domain.vo.mes import Mes
from informes.domain.bo.informe import Informe


class IInformeCommandRepository(ABC):
    @abstractmethod
    def del_mes(self, hogar_id: int, mes: Mes) -> Informe | None:
        """BLOQUEADO hasta el final de la transacción: dos generaciones a la vez no crean dos (uno por hogar y mes)."""

    @abstractmethod
    def guardar(self, informe: Informe, pdf: bytes) -> str | None:
        """Guarda el informe con su PDF nuevo. Devuelve el nombre del archivo que tenía (para borrarlo), o None."""
        ...
