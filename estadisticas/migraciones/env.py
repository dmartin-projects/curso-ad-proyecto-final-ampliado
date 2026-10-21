"""Alembic (las migraciones de SQLAlchemy): la URL y las tablas salen del propio servicio."""

from alembic import context

from estadisticas.ajustes import ajustes
from estadisticas.bd import Base, motor

config = context.config
target_metadata = Base.metadata  # para `alembic revision --autogenerate`


def run_migrations_offline() -> None:
    """`alembic upgrade head --sql`: imprime el SQL sin conectarse."""
    context.configure(url=ajustes().database_url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    with motor().connect() as conexion:
        context.configure(connection=conexion, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
