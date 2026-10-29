# asistente/domain/vo/filtro_de_movimientos.py — qué movimientos busca el asistente (módulo 95)
from dataclasses import dataclass
from datetime import date

from core.domain.exceptions.validacion_exception import ValidacionException


@dataclass(frozen=True, slots=True)
class FiltroDeMovimientos:
    desde: date
    hasta: date
    texto: str | None = None  # en el concepto, el comercio o las notas
    categoria_id: int | None = None  # una principal incluye sus subcategorías
    tipo: str | None = None  # "gasto" | "ingreso"

    def __post_init__(self):
        if self.desde > self.hasta:
            raise ValidacionException(f"'desde' ({self.desde}) es posterior a 'hasta' ({self.hasta}).")
