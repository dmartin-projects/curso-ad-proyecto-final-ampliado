# notificaciones/application/ports/i_traductor.py (módulo 88)
from abc import ABC, abstractmethod


class ITraductor(ABC):
    @abstractmethod
    def traducir(self, plantilla: object, idioma: str, contexto: dict) -> str:
        """`plantilla` es opaca para el núcleo (en Django, un texto perezoso de gettext con marcadores %(x)s)."""
