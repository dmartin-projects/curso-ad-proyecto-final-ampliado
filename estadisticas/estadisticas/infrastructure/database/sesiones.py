# estadisticas/infrastructure/database/sesiones.py — el motor y las sesiones de SQLAlchemy (módulos 85 y 89)
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from estadisticas.ajustes import ajustes


@lru_cache
def motor() -> Engine:
    # pool_pre_ping: si PostgreSQL se ha reiniciado, la conexión rota se descarta en vez de dar un error
    return create_engine(ajustes().database_url, pool_pre_ping=True, pool_size=5)


def sesion() -> Session:
    return sessionmaker(motor(), expire_on_commit=False)()
