# finanzas/application/exportar_movimientos_use_case/dtos/movimiento_exportado_output_dto.py (módulo 87)
from dataclasses import asdict, dataclass
from datetime import date
from decimal import Decimal

from finanzas.domain.read_models.movimiento_exportado import MovimientoExportado


@dataclass(frozen=True, slots=True)
class MovimientoExportadoOutputDTO:
    fecha: date
    concepto: str
    importe: Decimal
    cuenta: str
    categoria: str | None
    etiquetas: tuple[str, ...]

    @classmethod
    def desde_read_model(cls, rm: MovimientoExportado) -> "MovimientoExportadoOutputDTO":
        return cls(**asdict(rm))  # los mismos campos: el read model es del dominio; el OutputDTO, del use case
