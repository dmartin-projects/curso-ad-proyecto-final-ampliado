# asistente/domain/vo/estado_de_cuota.py — cuánto lleva gastado quien pregunta, y si puede seguir (módulo 98)
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from asistente.domain.enums.plan import Plan
from asistente.domain.exceptions.cuota_agotada_exception import CuotaAgotadaException
from asistente.domain.vo.cuota import Cuota


@dataclass(frozen=True, slots=True)
class EstadoDeCuota:
    plan: Plan
    cuota: Cuota
    tokens_hoy: int  # de esta persona en este hogar, desde las 00:00 del hogar
    coste_mes: Decimal  # de todo el hogar, desde el día 1 del mes del hogar
    manana: datetime  # cuándo vuelve a empezar el día (y la cuota de la persona)
    mes_siguiente: datetime  # cuándo vuelve a empezar el mes (y la del hogar)

    @property
    def tokens_restantes(self) -> int:
        return max(0, self.cuota.tokens_dia_persona - self.tokens_hoy)

    @property
    def agotada_persona(self) -> bool:
        return self.tokens_hoy >= self.cuota.tokens_dia_persona

    @property
    def agotada_hogar(self) -> bool:
        return self.coste_mes >= self.cuota.coste_mes_hogar

    def exigir(self, ahora: datetime) -> None:
        """Se comprueba ANTES de preguntar, con lo gastado hasta ahora: una pregunta empezada termina aunque se pase
        (cortarla a medias sería pagar por nada). Por eso la última del día puede pasarse un poco; el límite por
        pregunta (Limites.max_tokens, módulo 94) acota cuánto."""
        if self.agotada_hogar:
            raise CuotaAgotadaException(
                "El hogar ha llegado al límite del asistente de este mes.",
                segundos=_segundos(ahora, self.mes_siguiente),
                renueva=self.mes_siguiente.isoformat(),
            )
        if self.agotada_persona:
            raise CuotaAgotadaException(
                "Has llegado al límite de preguntas de hoy. Mañana vuelves a tenerlo.",
                segundos=_segundos(ahora, self.manana),
                renueva=self.manana.isoformat(),
            )


def _segundos(ahora: datetime, hasta: datetime) -> int:
    return max(1, int((hasta - ahora).total_seconds()))
