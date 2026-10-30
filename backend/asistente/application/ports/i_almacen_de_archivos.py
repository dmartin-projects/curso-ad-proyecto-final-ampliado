# asistente/application/ports/i_almacen_de_archivos.py — dónde se guardan adjuntos y exportaciones (módulo 97)
from abc import ABC, abstractmethod


class IAlmacenDeArchivos(ABC):
    """El almacenamiento de la app (S3/R2 en producción, el disco en desarrollo), visto desde el asistente."""

    @abstractmethod
    def guardar(self, carpeta: str, contenido: bytes) -> str:
        """Con un nombre nuevo (nunca el que manda el cliente) dentro de `carpeta`; devuelve la ruta."""

    @abstractmethod
    def url(self, ruta: str) -> str:
        """Una URL para descargarlo (en producción, firmada y con caducidad)."""

    @abstractmethod
    def borrar(self, ruta: str) -> None:
        """Si no existe, nada: borrar dos veces no es un error."""
