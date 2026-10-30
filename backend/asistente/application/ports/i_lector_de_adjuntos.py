# asistente/application/ports/i_lector_de_adjuntos.py — el texto de una foto o un PDF adjunto (módulo 97)
from abc import ABC, abstractmethod


class ILectorDeAdjuntos(ABC):
    """El OCR del módulo 74 (Tesseract, o la capa de texto de un PDF), visto desde el asistente."""

    @abstractmethod
    def leer(self, contenido: bytes, tipo: str) -> str:
        """El texto, tal cual (puede venir vacío: una foto sin texto)."""
