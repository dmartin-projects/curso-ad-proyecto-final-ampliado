"""Ejercicio 1 del módulo 87: una cuenta con movimientos no se borra (sin base de datos)."""

import pytest

from core.domain.enums.rol import Rol
from core.domain.exceptions.no_encontrado_exception import NoEncontradoException
from core.domain.exceptions.sin_permiso_exception import SinPermisoException
from finanzas.application.eliminar_cuenta_use_case.dtos.eliminar_cuenta_input_dto import EliminarCuentaInputDTO
from finanzas.domain.exceptions.cuenta_con_movimientos_exception import CuentaConMovimientosException
from finanzas.tests.fakes.mundo import HOGAR, OTRO_HOGAR, actor


def test_una_cuenta_con_movimientos_no_se_borra(mundo):
    mundo.movimiento()  # en la cuenta 10
    with pytest.raises(CuentaConMovimientosException) as e:
        mundo.eliminar_cuenta.ejecutar(EliminarCuentaInputDTO(HOGAR, actor(Rol.ADMIN), 10))
    assert e.value.status == 409 and e.value.campo is None
    mundo.eliminar_cuenta.ejecutar(EliminarCuentaInputDTO(HOGAR, actor(Rol.ADMIN), 11))  # vacía: sí
    assert not mundo.cuentas.existe(HOGAR, 11)


def test_permisos_y_hogar(mundo):
    with pytest.raises(SinPermisoException):
        mundo.eliminar_cuenta.ejecutar(EliminarCuentaInputDTO(HOGAR, actor(Rol.MIEMBRO), 11))
    with pytest.raises(NoEncontradoException):  # la 20 es de otro hogar
        mundo.eliminar_cuenta.ejecutar(EliminarCuentaInputDTO(HOGAR, actor(Rol.ADMIN), 20))
    assert mundo.cuentas.existe(OTRO_HOGAR, 20)
