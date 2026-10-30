# asistente/application/ports/i_fuente_de_ayuda.py — de dónde sale la ayuda (módulo 100)
from abc import ABC, abstractmethod


class IFuenteDeAyuda(ABC):
    @abstractmethod
    def documentos(self) -> dict[str, str]:
        """{nombre: Markdown}: en Gastos, los .md de asistente/ayuda/ (versionados con el código)."""
