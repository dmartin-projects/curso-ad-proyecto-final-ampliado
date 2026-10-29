# asistente/domain/read_models/serie_de_precios.py — la inflación oficial de un grupo de gasto, mes a mes (módulo 95)
from dataclasses import dataclass
from decimal import Decimal

from core.domain.vo.mes import Mes


@dataclass(frozen=True, slots=True)
class SerieDePrecios:
    grupo: str  # el código COICOP 2018 ("CP011") o "TOTAL"
    nombre: str  # como lo publica la fuente ("Food")
    tasas_anuales: dict[Mes, Decimal]  # % frente al mismo mes del año anterior; solo los meses ya publicados

    @property
    def ultimo_publicado(self) -> Mes | None:
        return max(self.tasas_anuales, default=None)
