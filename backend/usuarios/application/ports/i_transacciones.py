# usuarios/application/ports/i_transacciones.py — la transacción del social login, entre la ida y la vuelta (módulo 91)
from abc import ABC, abstractmethod

from usuarios.domain.vo.transaccion_social import TransaccionSocial


class ITransacciones(ABC):
    @abstractmethod
    def guardar(self, transaccion: TransaccionSocial) -> str:
        """La guarda unos minutos y devuelve una clave aleatoria (para la cookie del navegador)."""

    @abstractmethod
    def consumir(self, clave: str) -> TransaccionSocial | None:
        """La transacción de esa clave, UNA vez: la segunda, None. Caducada o inventada: None."""
