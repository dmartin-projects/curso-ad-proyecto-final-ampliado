# eventos/application/ports/i_outbox.py — el outbox, visto desde quien publica (módulos 85 y 88)
#
# El port que usan los PUBLICADORES de otras apps (finanzas, hogares): se lo da su contenedor como una pieza más, y
# en un test se puede cambiar por otra (un outbox roto, por ejemplo). Nunca habla con Kafka: guarda el mensaje en la
# MISMA transacción que el cambio que cuenta.
from abc import ABC, abstractmethod
from collections.abc import Iterable


class IOutbox(ABC):
    @abstractmethod
    def movimiento_guardado(self, m, *, creado: bool) -> None: ...

    @abstractmethod
    def movimiento_borrado(self, movimiento_id: int) -> None: ...

    @abstractmethod
    def movimientos_cambiados(self, ids: Iterable[int], *, tipo: str = "movimiento.actualizado") -> int:
        """Los cambios EN BLOQUE: lee el estado actual de esos ids (los que ya no existen, como tombstone)."""

    @abstractmethod
    def membresia_guardada(self, hogar_id: int, usuario_id: int, rol: str) -> None: ...

    @abstractmethod
    def membresia_borrada(self, hogar_id: int, usuario_id: int) -> None: ...
