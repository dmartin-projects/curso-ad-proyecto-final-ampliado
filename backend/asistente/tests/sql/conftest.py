"""Módulo 101: los tests del text-to-SQL con PostgreSQL de verdad y DOS conexiones (la de la app y la del rol)."""

import pytest
from django.core.management import call_command


@pytest.fixture(scope="session")
def rol_sql(django_db_setup, django_db_blocker):
    """La contraseña del rol (la migración lo crea sin login), una vez por sesión."""
    with django_db_blocker.unblock():
        call_command("preparar_rol_sql", verbosity=0)
