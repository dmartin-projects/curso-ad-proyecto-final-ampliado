# asistente/application/shared/dtos/cuota_output_dto.py (módulo 98)
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from asistente.domain.vo.estado_de_cuota import EstadoDeCuota


@dataclass(frozen=True, slots=True)
class CuotaOutputDTO:
    plan: str
    tokens_hoy: int
    tokens_dia: int
    coste_mes: Decimal
    coste_mes_maximo: Decimal
    agotada: bool
    agotada_por: str  # "persona" (la de hoy), "hogar" (la del mes) o "" (no está agotada)
    renueva: datetime  # cuándo se puede volver a preguntar (si está agotada), o cuándo empieza el día siguiente

    @classmethod
    def desde_estado(cls, e: EstadoDeCuota) -> "CuotaOutputDTO":
        return cls(
            plan=str(e.plan),
            tokens_hoy=e.tokens_hoy,
            tokens_dia=e.cuota.tokens_dia_persona,
            coste_mes=e.coste_mes,
            coste_mes_maximo=e.cuota.coste_mes_hogar,
            agotada=e.agotada_persona or e.agotada_hogar,
            agotada_por="hogar" if e.agotada_hogar else "persona" if e.agotada_persona else "",
            renueva=e.mes_siguiente if e.agotada_hogar else e.manana,
        )
