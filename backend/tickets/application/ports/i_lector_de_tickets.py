# tickets/application/ports/i_lector_de_tickets.py (módulo 88)
from abc import ABC, abstractmethod

from tickets.domain.vo.lectura import Lectura


class ILectorDeTickets(ABC):
    """El OCR (Tesseract, o la capa de texto de un PDF)."""

    @abstractmethod
    def leer(self, contenido: bytes, tipo_archivo: str) -> Lectura: ...
