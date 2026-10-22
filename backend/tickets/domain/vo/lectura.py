# tickets/domain/vo/lectura.py — lo que lee el OCR (módulos 74 y 88)
from dataclasses import dataclass

MIN_CARACTERES = 40  # por debajo, el OCR no ha leído nada útil


@dataclass(frozen=True)
class Lectura:
    """Lo que ha leído el OCR: el texto y la imagen leída (por si hay que enviársela a la IA)."""

    texto: str
    imagen_png: bytes = b""

    @property
    def es_util(self) -> bool:
        return len(self.texto.strip()) >= MIN_CARACTERES
