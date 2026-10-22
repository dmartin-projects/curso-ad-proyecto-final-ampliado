# estadisticas/infrastructure/database/models/movimiento_model.py — la tabla `movimientos` (módulos 85 y 89)
#
# Solo la conoce la infraestructura. El sufijo Model la distingue del business object (domain/bo/movimiento.py):
# en SQLAlchemy el nombre de la clase no está en ninguna migración (Alembic compara tablas y columnas).
from datetime import date
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, Index, Numeric, String, true
from sqlalchemy.orm import Mapped, mapped_column

from estadisticas.infrastructure.database.models.base import Base


class MovimientoModel(Base):
    __tablename__ = "movimientos"
    __table_args__ = (Index("movimientos_hogar_fecha", "hogar_id", "fecha"),)  # todas las consultas: hogar + fechas

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)  # el id de Django
    hogar_id: Mapped[int] = mapped_column(BigInteger)
    cuenta_id: Mapped[int] = mapped_column(BigInteger)
    fecha: Mapped[date] = mapped_column(Date)
    importe: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    categoria_id: Mapped[int | None] = mapped_column(BigInteger)
    comercio_id: Mapped[int | None] = mapped_column(BigInteger)
    origen: Mapped[str] = mapped_column(String(10))
    # Módulo 85, ejercicio 4. Las filas que existían antes de la migración 0002 recibieron True; para que
    # tengan el valor real se reconstruye desde los topics (ReconstruirProyeccionUseCase)
    revisado: Mapped[bool] = mapped_column(Boolean, server_default=true())
    version: Mapped[int] = mapped_column(BigInteger)  # el id del evento en el outbox: crece con cada cambio
