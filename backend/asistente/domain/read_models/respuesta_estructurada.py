# asistente/domain/read_models/respuesta_estructurada.py — la respuesta, en piezas para la interfaz (módulo 96)
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Cifra:
    concepto: str  # "Gasto de septiembre"
    importe: str  # tal como aparece en el texto: "776,59 €"


@dataclass(frozen=True, slots=True)
class RespuestaEstructurada:
    """El mismo contenido que el texto, con lo que una interfaz quiere pintar aparte: las cifras (para resaltarlas o
    fijarlas en el dashboard) y las preguntas de seguimiento (botones). Módulo 97: el chat."""

    texto: str
    cifras: tuple[Cifra, ...]
    seguimiento: tuple[str, ...]
