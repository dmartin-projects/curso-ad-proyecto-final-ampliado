# estadisticas/infrastructure/database/models/membresia_model.py — la tabla `membresias` (módulos 85 y 89)
from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from estadisticas.infrastructure.database.models.base import Base


class MembresiaModel(Base):
    __tablename__ = "membresias"

    hogar_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    rol: Mapped[str] = mapped_column(String(10))
    version: Mapped[int] = mapped_column(BigInteger)
