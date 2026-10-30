# asistente/domain/vo/trozo_de_ayuda.py — un trozo de la ayuda: lo que se indexa y se devuelve (módulo 100)
import hashlib
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TrozoDeAyuda:
    documento: str  # "importar-extractos"
    seccion: str  # "Sin duplicados"
    titulo: str  # el del documento: "Importar el extracto del banco"
    texto: str
    parte: int = 1  # una sección larga se parte en varios trozos

    @property
    def clave(self) -> str:
        """Única y estable: si el texto cambia, la clave es la misma (se actualiza); si cambia el título, es otra."""
        return f"{self.documento}#{self.seccion}#{self.parte}"

    @property
    def fuente(self) -> str:
        """Lo que se cita: «importar-extractos#Sin duplicados»."""
        return f"{self.documento}#{self.seccion}"

    @property
    def para_indexar(self) -> str:
        """Lo que se embebe y se busca: con el título del documento y de la sección delante, que dicen de qué va un trozo
        que por sí solo podría no decirlo ("Puedes subir el mismo dos veces…": ¿el mismo qué?)."""
        return f"{self.titulo}. {self.seccion}. {self.texto}"

    @property
    def huella(self) -> str:
        """Si no cambia, no se vuelve a embeber (indexar es incremental)."""
        return hashlib.sha256(self.para_indexar.encode()).hexdigest()[:16]
