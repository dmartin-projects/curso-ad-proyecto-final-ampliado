# estadisticas/domain/vo/mes.py — value object (módulo 89)
from dataclasses import dataclass
from datetime import date, datetime

from estadisticas.domain.exceptions.mes_mal_formado_exception import MesMalFormadoException


@dataclass(frozen=True, order=True, slots=True)
class Mes:
    """Un mes del calendario (value object): igual por valor, ordenable, y suma y resta meses."""

    anio: int
    numero: int

    def __post_init__(self):
        if not 1 <= self.numero <= 12:
            raise MesMalFormadoException(f"Mes {self.numero} fuera de 1-12")

    @classmethod
    def de(cls, fecha: date) -> "Mes":
        return cls(fecha.year, fecha.month)

    @classmethod
    def desde_texto(cls, texto: str) -> "Mes":
        """Del texto "2026-10" a Mes(2026, 10)."""
        try:
            return cls.de(datetime.strptime(texto, "%Y-%m"))
        except ValueError as e:
            raise MesMalFormadoException(f"{texto!r} no es un mes AAAA-MM") from e

    def mas(self, meses: int) -> "Mes":
        """Este mes más (o menos, si es negativo) `meses` meses."""
        total = self.anio * 12 + self.numero - 1 + meses
        return Mes(total // 12, total % 12 + 1)

    @property
    def primer_dia(self) -> date:
        return date(self.anio, self.numero, 1)

    def __str__(self) -> str:
        return f"{self.primer_dia:%Y-%m}"
