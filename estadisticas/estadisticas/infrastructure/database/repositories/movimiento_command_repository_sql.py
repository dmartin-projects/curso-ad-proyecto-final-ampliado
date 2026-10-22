# estadisticas/infrastructure/database/repositories/movimiento_command_repository_sql.py — IMovimientoCommandRepository
# con SQLAlchemy y PostgreSQL (módulo 89; las sentencias, del módulo 85)
from dataclasses import asdict

from sqlalchemy import delete, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from estadisticas.domain.bo.movimiento import Movimiento
from estadisticas.domain.repositories.i_movimiento_command_repository import IMovimientoCommandRepository
from estadisticas.infrastructure.database.guardado import ejecutar_escritura
from estadisticas.infrastructure.database.models.movimiento_model import MovimientoModel


class MovimientoCommandRepositorySQL(IMovimientoCommandRepository):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, movimiento: Movimiento) -> bool:
        fila = asdict(movimiento)
        # INSERT … ON CONFLICT DO UPDATE … WHERE: un "upsert" que solo pisa la fila si el evento es más nuevo
        sentencia = insert(MovimientoModel).values(fila)
        sentencia = sentencia.on_conflict_do_update(
            index_elements=[MovimientoModel.id],
            set_={k: getattr(sentencia.excluded, k) for k in fila if k != "id"},
            where=MovimientoModel.version < sentencia.excluded.version,
        ).returning(MovimientoModel.id)
        # RETURNING y no rowcount: en un upsert, el rowcount que da SQLAlchemy es -1 ("no lo sé")
        return ejecutar_escritura(self.sesion, sentencia).first() is not None

    def eliminar(self, movimiento_id: int, version: int) -> bool:
        sentencia = delete(MovimientoModel).where(
            MovimientoModel.id == movimiento_id, MovimientoModel.version < version
        )
        return ejecutar_escritura(self.sesion, sentencia).rowcount > 0

    def vaciar(self) -> None:
        self.sesion.execute(text("TRUNCATE movimientos"))
