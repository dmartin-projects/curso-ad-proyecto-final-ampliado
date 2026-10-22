# hogares/domain/repositories/i_hogar_command_repository.py (módulo 88)
from abc import ABC, abstractmethod

from hogares.domain.bo.hogar import Hogar


class IHogarCommandRepository(ABC):
    @abstractmethod
    def obtener(self, hogar_id: int) -> Hogar:
        """HogarNoEncontradoException si no existe (que sea TUYO lo comprueba quien pregunta: la view, por la membresía)."""

    @abstractmethod
    def guardar(self, hogar: Hogar) -> None: ...

    @abstractmethod
    def eliminar(self, hogar: Hogar) -> None:
        """Con todo lo suyo: la base de datos borra en cascada sus cuentas, movimientos, membresías…"""
