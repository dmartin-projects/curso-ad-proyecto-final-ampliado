# asistente/infrastructure/ayuda/fuente_de_ayuda_en_disco.py — los .md de la ayuda, del repositorio (módulo 100)
from pathlib import Path

from asistente.application.ports.i_fuente_de_ayuda import IFuenteDeAyuda

CARPETA = Path(__file__).resolve().parents[2] / "ayuda"


class FuenteDeAyudaEnDisco(IFuenteDeAyuda):
    def __init__(self, carpeta: Path = CARPETA):
        self.carpeta = carpeta

    def documentos(self):
        return {f.stem: f.read_text(encoding="utf-8") for f in sorted(self.carpeta.glob("*.md")) if f.stem != "README"}
