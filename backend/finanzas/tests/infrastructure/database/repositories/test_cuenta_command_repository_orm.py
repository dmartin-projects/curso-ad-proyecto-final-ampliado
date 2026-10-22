"""Ejercicio 1 del módulo 87: la carrera entre la comprobación del use case y el DELETE."""

import pytest

from conftest import CuentaFactory, MovimientoFactory
from finanzas.domain.exceptions.cuenta_con_movimientos_exception import CuentaConMovimientosException
from finanzas.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM

pytestmark = pytest.mark.django_db


def test_si_aparece_un_movimiento_entre_la_comprobacion_y_el_delete():
    cuenta = CuentaFactory()
    MovimientoFactory(cuenta=cuenta)
    with pytest.raises(CuentaConMovimientosException):  # el RESTRICT de la BD, traducido por el repositorio
        CuentaCommandRepositoryORM().eliminar(cuenta.hogar_id, cuenta.pk)
