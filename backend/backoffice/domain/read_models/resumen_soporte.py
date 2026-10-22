# backoffice/domain/read_models/resumen_soporte.py (módulo 88)
from dataclasses import dataclass

from backoffice.domain.read_models.por_estado import PorEstado


@dataclass(frozen=True, slots=True)
class ResumenSoporte:
    tickets_24h: tuple[PorEstado, ...]
    tickets_atascados: int
    importaciones_en_curso: int
    importaciones_con_error_7d: int
    hogares: int
    usuarios_activos: int
