# asistente/domain/read_models/conversion.py — un importe en otra moneda, con el tipo que se usó (módulo 95)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class Conversion:
    importe: Decimal
    de: str  # ISO 4217: "GBP"
    a: str
    resultado: Decimal
    tipo: Decimal  # 1 `de` = `tipo` `a`
    fecha_del_tipo: date  # el BCE publica los días laborables: la del sábado es la del viernes
