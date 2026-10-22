# informes/domain/bo/informe.py — el informe mensual en PDF (módulos 78 y 88)
from dataclasses import dataclass

from core.domain.vo.mes import Mes


@dataclass(eq=False)
class Informe:
    """Uno por hogar y mes: regenerarlo reemplaza su PDF (el nombre del archivo cambia: la caché no sirve el viejo)."""

    hogar_id: int
    mes: Mes
    archivo: str = ""
    tamano: int = 0
    generado_por_id: int | None = None  # None: lo generó Celery Beat, el día 1
    id: int | None = None

    @property
    def automatico(self) -> bool:
        return self.generado_por_id is None
