# asistente/domain/vo/precio.py — lo que cobra el proveedor por un modelo, y cuánto cuesta un Uso (módulo 93)
from dataclasses import dataclass
from decimal import Decimal

from asistente.domain.vo.uso import Uso

MILLON = Decimal(1_000_000)


@dataclass(frozen=True, slots=True)
class Precio:
    """Dólares por millón de tokens, como los publica el proveedor (cambian: van en los ajustes, con fecha)."""

    entrada: Decimal
    salida: Decimal  # el razonamiento se cobra como salida (ya está dentro de Uso.salida)
    cache: Decimal  # entrada servida desde la caché
    cache_escrita: Decimal | None = None  # ejercicio 1 del 106: escribir en la caché (None: como la entrada)

    def coste(self, uso: Uso) -> Decimal:
        sin_cache = uso.entrada - uso.cache - uso.cache_escrita
        escritura = self.entrada if self.cache_escrita is None else self.cache_escrita
        total = (
            sin_cache * self.entrada + uso.cache * self.cache + uso.cache_escrita * escritura + uso.salida * self.salida
        )
        return (total / MILLON).quantize(Decimal("0.000001"))
