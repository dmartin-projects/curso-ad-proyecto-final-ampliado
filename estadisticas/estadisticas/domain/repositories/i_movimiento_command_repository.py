# estadisticas/domain/repositories/i_movimiento_command_repository.py — el lado de ESCRITURA (CQRS, módulo 89)
#
# Lo que la proyección necesita para ESCRIBIR, sin decir cómo. Dos implementaciones: SQLAlchemy
# (infrastructure/database/repositories) y la de memoria (tests/fakes).
#
# LA REGLA de la proyección vive en el contrato de `guardar` y `eliminar`: solo cambia algo si el evento es MÁS
# NUEVO que lo guardado. Así da igual recibir un mensaje dos veces o releer el topic entero (idempotencia). Cada
# implementación la cumple a su manera, y los contract tests comprueban que las dos igual: la de SQLAlchemy, en
# UNA sentencia (sin "leer y luego escribir", que con dos consumidores sería una race condition).
from abc import ABC, abstractmethod

from estadisticas.domain.bo.movimiento import Movimiento


class IMovimientoCommandRepository(ABC):
    @abstractmethod
    def guardar(self, movimiento: Movimiento) -> bool:
        """Lo guarda si no existe o si su versión es más nueva que la guardada. True si lo ha guardado.
        EventoInvalidoException si la base de datos no lo puede guardar (un importe que no cabe…)."""

    @abstractmethod
    def eliminar(self, movimiento_id: int, version: int) -> bool:
        """Lo borra si la versión guardada es más vieja que `version`. True si lo ha borrado."""

    @abstractmethod
    def vaciar(self) -> None: ...
