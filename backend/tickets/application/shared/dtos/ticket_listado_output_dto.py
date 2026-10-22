# tickets/application/shared/dtos/ticket_listado_output_dto.py (módulo 88)
from dataclasses import asdict, dataclass
from datetime import date, datetime
from decimal import Decimal

from tickets.domain.read_models.ticket_listado import TicketListado


@dataclass(frozen=True, slots=True)
class LineaListadaOutputDTO:
    orden: int
    descripcion: str
    cantidad: Decimal
    precio_unitario: Decimal
    importe: Decimal


@dataclass(frozen=True, slots=True)
class GastoDelTicketOutputDTO:
    id: int
    fecha: date
    importe: Decimal
    concepto: str
    categoria_id: int | None
    revisado: bool


@dataclass(frozen=True, slots=True)
class TicketListadoOutputDTO:
    id: int
    estado: str
    cuenta_id: int
    nombre_original: str
    tipo: str
    archivo: str
    confianza: Decimal | None
    error: str
    datos_ia: dict
    intentos: int
    lineas: tuple[LineaListadaOutputDTO, ...]
    gasto: GastoDelTicketOutputDTO | None
    creado: datetime
    procesado_en: datetime | None

    @classmethod
    def desde_read_model(cls, rm: TicketListado) -> "TicketListadoOutputDTO":
        return cls(
            id=rm.id,
            estado=rm.estado,
            cuenta_id=rm.cuenta_id,
            nombre_original=rm.nombre_original,
            tipo=rm.tipo,
            archivo=rm.archivo,
            confianza=rm.confianza,
            error=rm.error,
            datos_ia=dict(rm.datos_ia),
            intentos=rm.intentos,
            lineas=tuple(LineaListadaOutputDTO(**asdict(li)) for li in rm.lineas),
            gasto=None if rm.gasto is None else GastoDelTicketOutputDTO(**asdict(rm.gasto)),
            creado=rm.creado,
            procesado_en=rm.procesado_en,
        )
