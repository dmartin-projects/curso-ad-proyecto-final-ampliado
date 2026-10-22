# eventos/domain/vo/mensaje.py — un mensaje del outbox (módulos 85 y 88)
from dataclasses import dataclass


@dataclass(frozen=True)
class Mensaje:
    """Un mensaje hacia Kafka: a qué topic, con qué clave (misma clave → misma partición → mismo orden) y qué valor."""

    topic: str
    clave: str
    tipo: str  # movimiento.creado, movimiento.actualizado, movimiento.eliminado, membresia.guardada…
    valor: dict | None  # None = "tombstone": este objeto ya no existe
