# informes/application/shared/dtos/informe_listado_output_dto.py (módulo 88)
from dataclasses import dataclass
from datetime import date, datetime

from informes.domain.read_models.informe_listado import InformeListado


@dataclass(frozen=True, slots=True)
class InformeListadoOutputDTO:
    id: int
    mes: date
    archivo: str
    tamano: int
    generado_por_id: int | None  # None: lo generó Celery Beat, el día 1
    creado: datetime
    actualizado: datetime

    @classmethod
    def desde_read_model(cls, rm: InformeListado) -> "InformeListadoOutputDTO":
        return cls(rm.id, rm.mes, rm.archivo, rm.tamano, rm.generado_por_id, rm.creado, rm.actualizado)
