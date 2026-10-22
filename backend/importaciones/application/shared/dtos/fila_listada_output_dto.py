# importaciones/application/shared/dtos/fila_listada_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from importaciones.domain.read_models.fila_listada import FilaListada


@dataclass(frozen=True, slots=True)
class FilaListadaOutputDTO:
    id: int
    numero: int
    fecha: date
    concepto: str
    importe: Decimal
    accion: str
    coincide_con_id: int | None
    coincide_con_concepto: str | None
    movimiento_id: int | None

    @classmethod
    def desde_read_model(cls, rm: FilaListada) -> "FilaListadaOutputDTO":
        return cls(**{campo: getattr(rm, campo) for campo in cls.__dataclass_fields__})
