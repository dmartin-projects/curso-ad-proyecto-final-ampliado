# finanzas/application/shared/dtos/movimiento_listado_output_dto.py (módulo 87)
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal

from finanzas.domain.read_models.movimiento_listado import MovimientoListado


@dataclass(frozen=True, slots=True)
class MovimientoListadoOutputDTO:
    id: int
    fecha: date
    importe: Decimal
    concepto: str
    cuenta_id: int
    cuenta_nombre: str
    categoria_id: int | None
    categoria_nombre: str | None
    categoria_color: str | None
    comercio_id: int | None
    comercio_nombre: str | None
    etiquetas: tuple[str, ...]
    notas: str
    origen: str
    revisado: bool
    num_adjuntos: int | None
    creado: datetime

    @classmethod
    def desde_read_model(cls, rm: MovimientoListado) -> "MovimientoListadoOutputDTO":
        return cls(**asdict(rm))  # los mismos campos: el read model es del dominio; el OutputDTO, del use case
