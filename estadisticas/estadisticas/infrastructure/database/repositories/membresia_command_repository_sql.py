# estadisticas/infrastructure/database/repositories/membresia_command_repository_sql.py — IMembresiaCommandRepository
# con SQLAlchemy y PostgreSQL (módulo 89; las sentencias, del módulo 85)
from dataclasses import asdict

from sqlalchemy import delete, text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from estadisticas.domain.bo.membresia import Membresia
from estadisticas.domain.repositories.i_membresia_command_repository import IMembresiaCommandRepository
from estadisticas.infrastructure.database.guardado import ejecutar_escritura
from estadisticas.infrastructure.database.models.membresia_model import MembresiaModel


class MembresiaCommandRepositorySQL(IMembresiaCommandRepository):
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def guardar(self, membresia: Membresia) -> bool:
        sentencia = insert(MembresiaModel).values(asdict(membresia))
        sentencia = sentencia.on_conflict_do_update(
            index_elements=[MembresiaModel.hogar_id, MembresiaModel.usuario_id],
            set_={"rol": sentencia.excluded.rol, "version": sentencia.excluded.version},
            where=MembresiaModel.version < sentencia.excluded.version,
        ).returning(MembresiaModel.hogar_id)
        return ejecutar_escritura(self.sesion, sentencia).first() is not None

    def eliminar(self, hogar_id: int, usuario_id: int, version: int) -> bool:
        sentencia = delete(MembresiaModel).where(
            MembresiaModel.hogar_id == hogar_id,
            MembresiaModel.usuario_id == usuario_id,
            MembresiaModel.version < version,
        )
        return ejecutar_escritura(self.sesion, sentencia).rowcount > 0

    def vaciar(self) -> None:
        self.sesion.execute(text("TRUNCATE membresias"))
