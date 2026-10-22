"""Las tablas de los modelos y las migraciones de Alembic dicen lo mismo (módulo 89): lo de `alembic check`."""

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from estadisticas.infrastructure.database.metadata import metadata
from estadisticas.infrastructure.database.sesiones import motor


def test_no_hay_cambios_sin_migracion():
    with motor().connect() as c:  # la base de datos de los tests, migrada con `alembic upgrade head` (conftest)
        assert compare_metadata(MigrationContext.configure(c), metadata) == []
