"""Contract tests de las cuentas (módulo 88): Django auth y los fakes, los mismos tests."""

import pytest

from usuarios.domain.enums.estado_cuenta import EstadoCuenta
from usuarios.domain.exceptions.email_ya_registrado_exception import EmailYaRegistradoException
from usuarios.infrastructure.auth.enlaces_django import EnlacesDjango
from usuarios.infrastructure.auth.politica_de_contrasenas_django import PoliticaDeContrasenasDjango
from usuarios.infrastructure.database.repositories.cuenta_command_repository_orm import CuentaCommandRepositoryORM
from usuarios.tests.fakes.cuenta_command_repository_fake import CuentaCommandRepositoryFake
from usuarios.tests.fakes.enlaces_fake import EnlacesFake
from usuarios.tests.fakes.politica_de_contrasenas_fake import PoliticaDeContrasenasFake


@pytest.fixture(params=["memoria", "orm"])
def piezas(request):
    if request.param == "memoria":
        return CuentaCommandRepositoryFake(), PoliticaDeContrasenasFake(), EnlacesFake()
    request.getfixturevalue("db")
    return CuentaCommandRepositoryORM(), PoliticaDeContrasenasDjango(), EnlacesDjango()


def test_registro_pendiente_completar_y_contrasenas(piezas):
    cuentas, politica, enlaces = piezas
    pk = cuentas.crear_pendiente(email="ana@example.com", nombre="Ana", apellidos="")
    assert cuentas.por_email("ANA@example.com") == pk and cuentas.por_email("luis@example.com") is None
    assert cuentas.estado(pk) is EstadoCuenta.PENDIENTE and not cuentas.comprobar_contrasena(pk, "")
    with pytest.raises(EmailYaRegistradoException):
        cuentas.crear_pendiente(email="ana@example.com", nombre="", apellidos="")
    cuentas.completar_registro(pk, "una-clave-muy-larga")
    assert cuentas.estado(pk) is EstadoCuenta.ACTIVA
    assert cuentas.comprobar_contrasena(pk, "una-clave-muy-larga") and not cuentas.comprobar_contrasena(pk, "otra")
    assert (
        politica.incumplimientos("corta", usuario_id=pk)
        and politica.incumplimientos("w9-Gz!kq-27-Lmp", usuario_id=pk) == []
    )

    enlace = enlaces.crear(pk, "nueva-password")
    uid, token = enlace.split("uid=")[1].split("&token=")
    assert enlaces.usuario_de(uid, token) == pk and enlaces.usuario_de(uid, "inventado") is None
    cuentas.cambiar_contrasena(pk, "w9-Gz!kq-27-Lmp")
    assert cuentas.comprobar_contrasena(pk, "w9-Gz!kq-27-Lmp")
