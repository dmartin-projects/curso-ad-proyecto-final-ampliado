"""Tests de infraestructura: PostgreSQL de verdad (la proyección usa INSERT … ON CONFLICT) y, los de Kafka, Kafka.

Dónde están: POSTGRES_TESTS (usuario:clave@host:puerto, por defecto el del compose de desarrollo) y
KAFKA_BOOTSTRAP_SERVERS (la variable del propio servicio, por defecto localhost:9092).
"""

import os
import time

import jwt
import psycopg
import pytest

# Antes de importar el servicio: su configuración se lee una vez (lru_cache)
BD_TEST = "estadisticas_test"
SERVIDOR = os.environ.get("POSTGRES_TESTS", "gastos:gastos@localhost:5432")
os.environ["DATABASE_URL"] = f"postgresql+psycopg://{SERVIDOR}/{BD_TEST}"
os.environ["JWT_SIGNING_KEY"] = "clave-de-los-tests-de-al-menos-32-bytes!!"


@pytest.fixture(scope="session", autouse=True)
def base_de_datos():
    """Crea la base de datos de los tests y le aplica las migraciones de Alembic (así también se prueban)."""
    with psycopg.connect(f"postgresql://{SERVIDOR}/postgres", autocommit=True) as c:
        c.execute(f"DROP DATABASE IF EXISTS {BD_TEST} WITH (FORCE)")
        c.execute(f"CREATE DATABASE {BD_TEST}")
    from alembic import command
    from alembic.config import Config

    command.upgrade(Config(os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")), "head")
    yield


@pytest.fixture(autouse=True)
def tablas_vacias():
    from sqlalchemy import text

    from estadisticas.infrastructure.database.sesiones import motor

    with motor().begin() as c:
        c.execute(text("TRUNCATE movimientos, membresias, progreso"))
    yield


@pytest.fixture
def token():
    """token(usuario_id) → un access token como los de Django (simplejwt: user_id en texto)."""

    def _token(usuario_id: int, *, tipo="access", caduca_en=600, clave=os.environ["JWT_SIGNING_KEY"]):
        ahora = int(time.time())
        datos = {"token_type": tipo, "exp": ahora + caduca_en, "iat": ahora, "jti": "x", "user_id": str(usuario_id)}
        return jwt.encode(datos, clave, algorithm="HS256")

    return _token
