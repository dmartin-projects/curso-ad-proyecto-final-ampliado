# asistente/domain/vo/contenido_retirado.py — un texto de terceros que no llega al modelo (módulo 102)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ContenidoRetirado:
    """Un artefacto más (como un gráfico): para la interfaz, que avisa a la persona. El texto retirado no viaja ni
    aquí: si el aviso lo repitiera, lo leería otra vez quien no debe (por ejemplo, el Markdown descargado)."""

    origen: str  # la tool que lo trajo ("detalle_ticket", "buscar_movimientos"…) o "adjunto"
    puntuacion: float  # la del clasificador, de 0 a 1

    @property
    def texto(self) -> str:
        donde = "el documento adjunto" if self.origen == "adjunto" else f"lo que ha devuelto {self.origen}"
        return f"He descartado {donde}: contenía texto que parecía instrucciones para mí, no datos."
