# tickets/application/ports/i_extractor_de_datos.py (módulo 88)
from abc import ABC, abstractmethod

from tickets.domain.vo.datos_ticket import DatosTicket


class IExtractorDeDatos(ABC):
    """La IA: del texto (y la imagen, si el OCR no ha servido) a datos. DatosIlegiblesException si responde algo
    inservible; los errores pasajeros (red, 429, 503, circuito abierto) se propagan tal cual: los reintenta la tarea."""

    @abstractmethod
    def extraer(self, texto: str, categorias: list[str], imagen_png: bytes | None = None) -> DatosTicket: ...
