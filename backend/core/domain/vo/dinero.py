# core/domain/vo/dinero.py — value object (módulo 87)
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

CENTIMO = Decimal("0.01")


@dataclass(frozen=True, slots=True, order=True)
class Dinero:
    """Un importe en la moneda del hogar, siempre en céntimos exactos.

    Inmutable y comparable por valor: dos Dinero("10") son el mismo dinero. Se redondea al céntimo
    "como en la tienda" (ROUND_HALF_UP: 0,005 → 0,01), no al par (el redondeo por defecto de Decimal).
    Nunca float: 0.1 + 0.2 no es 0.3 y un céntimo perdido en una suma de 2.000 gastos se nota.
    """

    cantidad: Decimal

    def __post_init__(self):
        if isinstance(self.cantidad, float):
            raise TypeError("Dinero no acepta float: usa Decimal o str")
        object.__setattr__(self, "cantidad", Decimal(self.cantidad).quantize(CENTIMO, rounding=ROUND_HALF_UP))

    @classmethod
    def cero(cls) -> "Dinero":
        return cls(Decimal(0))

    @property
    def es_cero(self) -> bool:
        return self.cantidad == 0

    @property
    def es_gasto(self) -> bool:
        """En Gastos, un importe negativo es un gasto y uno positivo, un ingreso."""
        return self.cantidad < 0

    def __add__(self, otro: "Dinero") -> "Dinero":
        return Dinero(self.cantidad + otro.cantidad)

    def __sub__(self, otro: "Dinero") -> "Dinero":
        return Dinero(self.cantidad - otro.cantidad)

    def __neg__(self) -> "Dinero":
        return Dinero(-self.cantidad)

    def __abs__(self) -> "Dinero":
        return Dinero(abs(self.cantidad))

    def __str__(self) -> str:
        return str(self.cantidad)  # "-12.50": el mismo texto que el Decimal de la base de datos
