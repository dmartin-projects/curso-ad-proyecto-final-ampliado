# core/domain/vo/mes.py — value object (módulo 87)
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True, slots=True, order=True)
class Mes:
    """Un mes del calendario: el periodo de los presupuestos, el dashboard y los informes.

    Sustituye a las fechas "siempre día 1" y a las funciones sueltas rango_mes / mes_anterior: un
    Mes no puede ser el día 15, y "el mes siguiente a diciembre" se calcula en un solo sitio.
    """

    anio: int
    numero: int

    def __post_init__(self):
        if not 1 <= self.numero <= 12:
            raise ValueError(f"Mes no válido: {self.numero}")

    @classmethod
    def de(cls, fecha: date) -> "Mes":
        return cls(fecha.year, fecha.month)

    @classmethod
    def desde_texto(cls, texto: str) -> "Mes":
        """'2026-10' → Mes(2026, 10)"""
        anio, numero = texto.split("-")[:2]
        return cls(int(anio), int(numero))

    @property
    def inicio(self) -> date:
        return date(self.anio, self.numero, 1)

    @property
    def fin(self) -> date:
        """El primer día del mes siguiente: los rangos son [inicio, fin), sin pelearse con días 28, 30 o 31."""
        return self.siguiente().inicio

    def siguiente(self) -> "Mes":
        return Mes(self.anio + (self.numero == 12), self.numero % 12 + 1)

    def anterior(self) -> "Mes":
        return Mes(self.anio - (self.numero == 1), (self.numero - 2) % 12 + 1)

    def ultimos(self, n: int) -> list["Mes"]:
        """Los n meses que terminan en este, del más antiguo al más reciente."""
        meses = [self]
        for _ in range(n - 1):
            meses.insert(0, meses[0].anterior())
        return meses

    def contiene(self, fecha: date) -> bool:
        return self.inicio <= fecha < self.fin

    def __str__(self) -> str:
        return f"{self.anio:04d}-{self.numero:02d}"
