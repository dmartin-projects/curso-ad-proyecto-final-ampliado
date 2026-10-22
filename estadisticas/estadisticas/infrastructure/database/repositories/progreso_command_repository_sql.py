# estadisticas/infrastructure/database/repositories/progreso_command_repository_sql.py — IProgresoCommandRepository
# con SQLAlchemy y PostgreSQL (módulo 89; la sentencia, del módulo 85)
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from estadisticas.domain.repositories.i_progreso_command_repository import IProgresoCommandRepository
from estadisticas.infrastructure.database.models.progreso_model import ProgresoModel


class ProgresoCommandRepositorySQL(IProgresoCommandRepository):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, topic: str, particion: int, offset: int, marca: datetime) -> None:
        fila = insert(ProgresoModel).values(topic=topic, particion=particion, offset=offset, marca=marca)
        self.sesion.execute(fila.on_conflict_do_update(index_elements=["topic", "particion"], set_=fila.excluded))

    def vaciar(self) -> None:
        self.sesion.execute(text("TRUNCATE progreso"))
