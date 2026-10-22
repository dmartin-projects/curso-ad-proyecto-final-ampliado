# estadisticas/infrastructure/database/repositories/membresia_query_service_sql.py — IMembresiaQueryService con
# SQLAlchemy (módulo 89; la consulta, del módulo 85)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from estadisticas.domain.repositories.i_membresia_query_service import IMembresiaQueryService
from estadisticas.infrastructure.database.models.membresia_model import MembresiaModel


class MembresiaQueryServiceSQL(IMembresiaQueryService):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def es_miembro(self, hogar_id: int, usuario_id: int) -> bool:
        return bool(
            self.sesion.scalar(
                select(func.count()).where(MembresiaModel.hogar_id == hogar_id, MembresiaModel.usuario_id == usuario_id)
            )
        )
