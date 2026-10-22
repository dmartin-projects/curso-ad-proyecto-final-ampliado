# finanzas/domain/repositories/i_cuenta_command_repository.py (módulo 87)
from abc import ABC, abstractmethod


class ICuentaCommandRepository(ABC):
    @abstractmethod
    def existe(self, hogar_id: int, cuenta_id: int) -> bool: ...
