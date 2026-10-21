"""SQLAlchemy 2: el motor, las sesiones y las tablas del servicio."""

from datetime import date, datetime
from decimal import Decimal
from functools import lru_cache

from sqlalchemy import BigInteger, Date, DateTime, Index, Integer, Numeric, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from .ajustes import ajustes


class Base(DeclarativeBase):
    pass


class Movimiento(Base):
    """Proyección: lo que el servicio sabe de cada movimiento, tal como llegó en su último evento."""

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
    version: Mapped[int] = mapped_column(BigInteger)  # el id del evento en el outbox: crece con cada cambio


class Membresia(Base):
    """Quién es miembro de qué hogar: para decidir quién puede ver qué, sin preguntar a Django."""

    __tablename__ = "membresias"

    hogar_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    rol: Mapped[str] = mapped_column(String(10))
    version: Mapped[int] = mapped_column(BigInteger)


class Progreso(Base):
    """Hasta dónde ha llegado la proyección en cada partición (para decir "datos de hace X segundos")."""

    __tablename__ = "progreso"

    topic: Mapped[str] = mapped_column(String(100), primary_key=True)
    particion: Mapped[int] = mapped_column(Integer, primary_key=True)
    offset: Mapped[int] = mapped_column(BigInteger)
    marca: Mapped[datetime] = mapped_column(DateTime(timezone=True))  # cuándo se publicó el último aplicado


@lru_cache
def motor():
    # pool_pre_ping: si PostgreSQL se ha reiniciado, la conexión rota se descarta en vez de dar un error
    return create_engine(ajustes().database_url, pool_pre_ping=True, pool_size=5)


def sesion() -> Session:
    return sessionmaker(motor(), expire_on_commit=False)()
