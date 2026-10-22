# estadisticas/infrastructure/database/repositories/progreso_query_service_sql.py — IProgresoQueryService con
# SQLAlchemy (módulo 89; la consulta, del módulo 85)
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from estadisticas.domain.repositories.i_progreso_query_service import IProgresoQueryService
from estadisticas.infrastructure.database.models.progreso_model import ProgresoModel


class ProgresoQueryServiceSQL(IProgresoQueryService):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def ultimo_evento(self) -> datetime | None:
        return self.sesion.scalar(select(func.max(ProgresoModel.marca)))
