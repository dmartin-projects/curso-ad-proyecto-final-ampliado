# estadisticas/infrastructure/database/models/progreso_model.py — la tabla `progreso` (módulos 85 y 89)
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from estadisticas.infrastructure.database.models.base import Base


class ProgresoModel(Base):
    __tablename__ = "progreso"

    topic: Mapped[str] = mapped_column(String(100), primary_key=True)
    particion: Mapped[int] = mapped_column(Integer, primary_key=True)
    offset: Mapped[int] = mapped_column(BigInteger)
    marca: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # cuándo se publicó el último aplicado
